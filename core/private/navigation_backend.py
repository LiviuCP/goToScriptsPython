import os, json
from pathlib import Path
from settings import navigation_settings as navset
from utilities import common
from .private import nav_cmd_common as nvcdcmn

class NavigationBackend(nvcdcmn.NavCmdCommon):
    def __init__(self):
        super().__init__(navset)
        self.excludedHistory = {}
        self.favorites = []
        self.addedToFavorites = []
        self.removedFromFavorites = []
        self.__loadFiles__()
        self.__doHistoryCleanup__()
        self.__consolidateHistory__()
        self.__computeFavorites__()

    def clearHistory(self):
        super().clearHistory()
        # favorites are not erased but the corresponding excluded history should have the visits count reset for each included path
        for path in self.excludedHistory:
            self.excludedHistory[path] = 0

    def chooseFavoritesMenuEntry(self, userInput):
        return self.__retrieveMenuEntry__(userInput, self.favorites)

    def buildFilteredFavorites(self, filterKey, filteredContent):
        assert len(filterKey) > 0, "Empty filter key found"
        return nvcdcmn.buildFilteredHistory(self.excludedHistory.keys(), filterKey, navset.max_filtered_fav_entries, filteredContent)

    def getFavoritesInfo(self):
        return self.favorites.copy()

    def isFavoritesMenuEmpty(self):
        return len(self.excludedHistory) == 0

    def addPathToFavorites(self, pathToAdd):
        assert len(pathToAdd) > 0, "Empty path argument detected"
        shouldAddToFavorites = True
        for path in self.excludedHistory:
            if path.lower() == pathToAdd.lower():
                shouldAddToFavorites = False
                break
        if shouldAddToFavorites:
            nrOfPathVisits = self.persistentHistory.get(pathToAdd)
            if nrOfPathVisits is not None:
                del self.persistentHistory[pathToAdd]
                self.__consolidateHistory__()
            else:
                nrOfPathVisits = 0
            self.excludedHistory[pathToAdd] = nrOfPathVisits
            if pathToAdd in self.removedFromFavorites:
                self.removedFromFavorites.remove(pathToAdd)
            self.addedToFavorites.append(pathToAdd)
            self.__computeFavorites__()
        return shouldAddToFavorites

    def removePathFromFavorites(self, pathToRemove):
        pathRemoved = False
        # remove from excluded history, update favorites; move to persistent history if visited at least once
        if pathToRemove in self.favorites:
            assert pathToRemove in self.excludedHistory, "Favorites path not contained in excluded history!"
            nrOfRemovedPathVisits = self.excludedHistory[pathToRemove]
            if nrOfRemovedPathVisits > 0:
                self.persistentHistory[pathToRemove] = nrOfRemovedPathVisits
                self.__consolidateHistory__()
            del self.excludedHistory[pathToRemove]
            if pathToRemove in self.addedToFavorites:
                self.addedToFavorites.remove(pathToRemove)
            self.removedFromFavorites.append(pathToRemove)
            self.__computeFavorites__()
            pathRemoved = True
        return pathRemoved

    def removeMissingDir(self, pathToRemove):
        assert len(pathToRemove) > 0, "Empty path argument detected"
        self.__checkAndHandleOutdatedDailyLog__()
        self.__removeFromDailyLog__(pathToRemove)
        removedFromRecentHistory = False
        if pathToRemove in self.recentHistory:
            self.recentHistory.remove(pathToRemove)
            removedFromRecentHistory = True
        removedFromPersistentHistory = False
        if pathToRemove in self.persistentHistory:
            del self.persistentHistory[pathToRemove]
            removedFromPersistentHistory = True
        elif pathToRemove in self.excludedHistory:
            del self.excludedHistory[pathToRemove]
            self.__computeFavorites__()
        else:
            assert False, "Removed entry neither present in persistent, nor in excluded history!"
        if removedFromRecentHistory or removedFromPersistentHistory:
            self.__consolidateHistory__()
        return pathToRemove

    def mapMissingDir(self, replacedPath, replacingPath):
        replacedPathInPHist = (replacedPath in self.persistentHistory)
        assert replacedPathInPHist or replacedPath in self.excludedHistory, "Path to replace not found in persistent/excluded history!"
        assert len(replacingPath) > 0, "Empty replacing path argument detected!"
        replacedPathInRHist = (replacedPath in self.recentHistory)
        # handle path to replace: remove it from all required files
        self.__checkAndHandleOutdatedDailyLog__()
        self.__removeFromDailyLog__(replacedPath)
        if replacedPathInRHist:
            self.recentHistory.remove(replacedPath)
        replacedPathVisits = self.persistentHistory.pop(replacedPath) if replacedPathInPHist else self.excludedHistory.pop(replacedPath)
        # handle replacing path
        replacingPathVisits = 0
        replacingPathVisitsIncreasedInPHist = False
        if replacingPath in self.persistentHistory:
            replacingPathVisits = self.persistentHistory[replacingPath]
            if replacedPathVisits > replacingPathVisits:
                self.persistentHistory[replacingPath] = replacedPathVisits
                replacingPathVisitsIncreasedInPHist = True
        elif replacingPath in self.excludedHistory:
            replacingPathVisits = self.excludedHistory[replacingPath]
            if replacedPathVisits > replacingPathVisits:
                self.excludedHistory[replacingPath] = replacedPathVisits
        else: # new path, neither contained in history, nor in favorites (possibly old directory renamed or newly created directory)
            if replacedPathInPHist:
                self.persistentHistory[replacingPath] = replacedPathVisits
            else:
                self.excludedHistory[replacingPath] = replacedPathVisits
        # final touch: consolidate history, recompute favorites
        if replacedPathInRHist or replacedPathInPHist or replacingPathVisitsIncreasedInPHist:
            self.__consolidateHistory__()
        if not replacedPathInPHist:
            self.__computeFavorites__()
        return (replacedPath, replacingPath)

    def __loadFiles__(self):
        super().__loadFiles__()
        self.excludedHistory.clear()
        if os.path.isfile(self.settings.e_hist_file):
            with open(self.settings.e_hist_file, "r") as e_hist:
                excludedHistoryAsJSON = e_hist.readline()
                try:
                    self.excludedHistory = json.loads(excludedHistoryAsJSON)
                except json.JSONDecodeError:
                    print(f"Invalid JSON file format in file: {self.settings.e_hist_file}")

    def __saveFiles__(self):
        super().__saveFiles__()
        with open(self.settings.e_hist_file, "w") as e_hist:
            excludedHistoryAsJSON = json.dumps(self.excludedHistory)
            e_hist.write(excludedHistoryAsJSON)

    def __reconcileFiles__(self):
        currentRecentHistory = self.recentHistory.copy()
        currentPersistentHistory = self.persistentHistory.copy()
        currentExcludedHistory = self.excludedHistory.copy()
        currentDailyLog = self.dailyLog.copy()
        self.__loadFiles__() # reload history files of previous session
        self.recentHistory = currentRecentHistory # restore current recent history
        # current recent history overrides the recent history of previous session, however the no longer existing paths should be removed
        for path in self.recentHistory[:]:
            if not os.path.exists(path):
                self.recentHistory.remove(path)
        # add current persistent history content to persistent/excluded history of previous session, reconcile number of visits
        for path, visitsCount in currentPersistentHistory.items():
            if path in self.persistentHistory:
                if visitsCount > self.persistentHistory[path]:
                    self.persistentHistory[path] = visitsCount
            elif path in self.excludedHistory:
                newVisitsCount = visitsCount if visitsCount > self.excludedHistory[path] else self.excludedHistory[path]
                if path in self.removedFromFavorites:
                    self.persistentHistory[path] = newVisitsCount
                    del self.excludedHistory[path]
                else:
                    self.excludedHistory[path] = newVisitsCount
            elif os.path.exists(path):
                self.persistentHistory[path] = visitsCount
            else:
                pass # discard entry by not adding it back to resulting (reconciled) persistent history
        # add current excluded history content to excluded/persistent history of previous session, reconcile number of visits
        for path, visitsCount in currentExcludedHistory.items():
            if path in self.excludedHistory:
                if visitsCount > self.excludedHistory[path]:
                    self.excludedHistory[path] = visitsCount
            elif path in self.persistentHistory:
                newVisitsCount = visitsCount if visitsCount > self.persistentHistory[path] else self.persistentHistory[path]
                if path in self.addedToFavorites:
                    self.excludedHistory[path] = newVisitsCount
                    del self.persistentHistory[path]
                else:
                    self.persistentHistory[path] = newVisitsCount
            elif os.path.exists(path):
                self.excludedHistory[path] = visitsCount
            else:
                pass # discard entry by not adding it back to resulting (reconciled) excluded history
        # remove paths from resulting persistent history that neither exist any longer nor are contained within persistent/excluded history of the current session
        persistentHistoryPathsToDelete = []
        for path in self.persistentHistory:
            if not (path in currentPersistentHistory or path in currentExcludedHistory or os.path.exists(path)):
                persistentHistoryPathsToDelete.append(path)
        for path in persistentHistoryPathsToDelete:
            del self.persistentHistory[path]
        # remove paths from resulting excluded history that neither exist any longer nor are contained within excluded/persistent history of the current session
        excludedHistoryPathsToDelete = []
        for path in self.excludedHistory:
            if not (path in currentPersistentHistory or path in currentExcludedHistory or os.path.exists(path)):
                excludedHistoryPathsToDelete.append(path)
        for path in excludedHistoryPathsToDelete:
            del self.excludedHistory[path]
        # daily logs of current and previous session to be consolidated; any entry that is not contained within reconciled persistent/excluded history should be removed
        dailyLogPathsToDelete = []
        for path in self.dailyLog:
            if not (path in self.persistentHistory or path in self.excludedHistory):
                dailyLogPathsToDelete.append(path)
        for path in dailyLogPathsToDelete:
            self.dailyLog.remove(path)
        for path in currentDailyLog:
            if not path in self.dailyLog and (path in self.persistentHistory or path in self.excludedHistory):
                self.dailyLog.add(path)

    def __relevantFilesModifiedAfterStartup__(self):
        return super().__relevantFilesModifiedAfterStartup__() or (os.path.isfile(navset.e_hist_file) and os.path.getmtime(navset.e_hist_file) > self.openingTime)

    def __doHistoryCleanup__(self):
        # clean up persistent history (except the most visited paths)
        if len(self.persistentHistory) > navset.p_hist_max_entries:
            persistentHistorySortedPaths = []
            for path, visitsCount in sorted(self.persistentHistory.items(), key = lambda k:(k[1], k[0].lower()), reverse = True):
                persistentHistorySortedPaths.append(path)
            for index in range(navset.p_hist_max_entries, len(persistentHistorySortedPaths)):
                currentPath = persistentHistorySortedPaths[index]
                if not os.path.exists(currentPath):
                    del self.persistentHistory[currentPath]
        # clean up recent history
        for path in self.recentHistory[:]:
            if not os.path.exists(path):
                self.recentHistory.remove(path)

    def __updatePermanentHistory__(self, dirPath):
        if dirPath in self.excludedHistory.keys():
            self.excludedHistory[dirPath] += 1
        else:
            self.__updatePersistentHistory__(dirPath)

    def __consolidateHistory__(self):
        pHistDict = {}
        limit = 0
        for path, visitsCount in sorted(self.persistentHistory.items(), key = lambda k:(k[1], k[0].lower()), reverse = True):
            if (limit == navset.p_hist_max_entries):
                break
            pHistDict[path] = os.path.basename(path)
            limit += 1
        chosenPHistPaths = []
        for path, basenm in sorted(pHistDict.items(), key = lambda k:(k[1].lower(), k[0].lower())):
            chosenPHistPaths.append(path)
        self.__doConsolidateHistory__(chosenPHistPaths)

    def __computeFavorites__(self):
        favDict = {}
        for path in self.excludedHistory:
            favDict[path] = os.path.basename(path)
        self.favorites.clear()
        for path, dirName in sorted(favDict.items(), key = lambda k:(k[1].lower(), k[0].lower())):
            self.favorites.append(path)

    def __retrieveMenuEntry__(self, userInput, content):
        unused = "" # this variable is part of a tuple that has been kept in this form for (legacy) compatibility
        # access parent dir of menu entry
        if len(userInput) > 1 and userInput[0] == "," and common.isValidMenuEntryNr(userInput[1:], content):
            output = str(Path(content[int(userInput[1:])-1].strip("\n")).parent)
            userInput = ":parent" # used for further differentiation between entry directory and parent in case the returned path is invalid
        # retrieved path to be used for setting target dir from menu
        elif len(userInput) > 1 and userInput[0] == "+" and common.isValidMenuEntryNr(userInput[1:], content):
            output = str(Path(content[int(userInput[1:])-1].strip("\n")))
            userInput = ":preceding+" # used for further differentiation between entry directory and parent for setting target dir
        # retrieved parent path to be used for setting target dir from menu
        elif len(userInput) > 1 and userInput[0] == "-" and common.isValidMenuEntryNr(userInput[1:], content):
            output = str(Path(content[int(userInput[1:])-1].strip("\n")).parent)
            userInput = ":preceding-" # used for further differentiation between entry directory and parent for setting target dir
        else:
            output, userInput, unused = super().__retrieveMenuEntry__(userInput, content)
        return (output, userInput, unused)

def isHomeDirectoryPath(dirPath):
    assert len(dirPath) > 0, "Empty directory path!"
    return os.path.normpath(dirPath) == os.path.normpath(navset.home_dir)
