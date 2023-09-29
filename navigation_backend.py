import sys, os
import nav_cmd_common as nvcdcmn, navigation_settings as navset, system_settings as sysset

class NavigationBackend:
    def __init__(self):
        self.recentHistory = []
        self.persistentHistory = {}
        self.excludedHistory = {}
        self.dailyLog = []
        self.consolidatedHistory = []
        self.favorites = []
        self.__loadNavigationFiles()
        self.__doHistoryCleanup()
        self.__consolidateHistory()
        self.__computeFavorites()

    def getConsolidatedHistoryInfo(self):
        return (self.consolidatedHistory.copy(), len(self.recentHistory))

    def getFavorites(self):
        return self.favorites.copy()

    def choosePath(self, menuChoice, userInput, filteredContent):
        content = filteredContent if menuChoice in ["-fh", "-ff"] else self.favorites if menuChoice == "-f" else self.consolidatedHistory
        return nvcdcmn.getMenuEntry(userInput, content)

    def isMenuEmpty(self, menuChoice):
        assert menuChoice in ["-h", "-f"], "Invalid menu option argument detected"
        return len(self.excludedHistory if menuChoice == "-f" else self.consolidatedHistory) == 0

    def updateNavigationHistory(self, dirPath):
        assert len(dirPath) > 0, "Empty path argument detected"
        # handle recent history
        if dirPath in self.recentHistory:
            self.recentHistory.remove(dirPath)
        elif len(self.recentHistory) == navset.r_hist_max_entries:
            self.recentHistory.pop(len(self.recentHistory)-1)
        self.recentHistory = [dirPath] + self.recentHistory
        # handle persistent/excluded history
        if dirPath not in self.dailyLog:
            self.dailyLog.append(dirPath)
            if dirPath in self.excludedHistory.keys():
                self.excludedHistory[dirPath] += 1
            elif dirPath in self.persistentHistory.keys():
                self.persistentHistory[dirPath] += 1
            else:
                self.persistentHistory[dirPath] = 1
        self.__consolidateHistory()

    def clearHistory(self):
        self.recentHistory.clear()
        self.persistentHistory.clear()
        self.consolidatedHistory.clear()
        self.dailyLog.clear()
        # favorites are not erased but the corresponding excluded history should have the visits count reset for each included path
        for path in self.excludedHistory.keys():
            self.excludedHistory[path] = 0

    def buildFilteredNavigationHistory(self, filterKey, filteredContent):
        assert len(filterKey) > 0, "Empty filter key found"
        return nvcdcmn.buildFilteredPersistentHistory(self.persistentHistory, filterKey, navset.max_filtered_hist_entries, filteredContent)

    def buildFilteredFavorites(self, filterKey, filteredContent):
        assert len(filterKey) > 0, "Empty filter key found"
        return nvcdcmn.buildFilteredHistory(self.excludedHistory.keys(), filterKey, navset.max_filtered_fav_entries, filteredContent)

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
                self.__consolidateHistory()
            else:
                nrOfPathVisits = 0
            self.excludedHistory[pathToAdd] = nrOfPathVisits
            self.__computeFavorites()
        return shouldAddToFavorites

    def removePathFromFavorites(self, pathToRemove):
        pathRemoved = False
        # remove from excluded history, update favorites; move to persistent history if visited at least once
        if pathToRemove in self.favorites:
            assert pathToRemove in self.excludedHistory, "Favorites path not contained in excluded history!"
            nrOfRemovedPathVisits = self.excludedHistory[pathToRemove]
            if nrOfRemovedPathVisits > 0:
                self.persistentHistory[pathToRemove] = nrOfRemovedPathVisits
                self.__consolidateHistory()
            del self.excludedHistory[pathToRemove]
            self.__computeFavorites()
            pathRemoved = True
        return pathRemoved

    def isValidQuickNavHistoryEntryNr(self, userInput):
        isValid = False
        if len(userInput) > 0 and userInput.isdigit():
            quickNavEntryNr = int(userInput)
            isValid = quickNavEntryNr > 0 and quickNavEntryNr <= len(self.recentHistory) and quickNavEntryNr <= navset.q_hist_max_entries
        return isValid

    def removeMissingDir(self, pathToRemove):
        assert len(pathToRemove) > 0, "Empty path argument detected"
        if pathToRemove in self.dailyLog:
            self.dailyLog.remove(pathToRemove)
        removedFromRecentHistory = False
        if pathToRemove in self.recentHistory:
            self.recentHistory.remove(pathToRemove)
            removedFromRecentHistory = True
        removedFromPersistentHistory = False
        if pathToRemove in self.persistentHistory:
            del self.persistentHistory[pathToRemove]
            removedFromPersistentHistory = True
        elif pathTorRemove in self.excludedHistory:
            del self.excludedHistory[pathToRemove]
            self.__computeFavorites()
        else:
            assert False, "Removed entry neither present in persistent, nor in excluded history!"
        if removedFromRecentHistory or removedFromPersistentHistory:
            self.__consolidateHistory()
        return pathToRemove

    def mapMissingDir(self, replacedPath, replacingPath):
        assert len(replacedPath) > 0, "Empty argument for 'replaced path' detected"
        assert len(replacingPath) > 0, "Empty argument for 'replacing path' detected"
        replacedPathVisits = 0
        replacingPathVisits = 0
        replacedPathInRHist = False
        replacedPathInPHist = False
        replacedPathInEHist = False
        replacingPathVisitsIncreasedInPHist = False
        # handle path to replace: remove it from all required files
        if replacedPath in self.dailyLog:
            self.dailyLog.remove(replacedPath)
        if replacedPath in self.recentHistory:
            self.recentHistory.remove(replacedPath)
            replacedPathInRHist = True
        if replacedPath in self.persistentHistory:
            replacedPathVisits = self.persistentHistory[replacedPath]
            self.persistentHistory.pop(replacedPath)
            replacedPathInPHist = True
        else:
            #only modify the excluded history for the moment, to be removed from favorites in next step
            replacedPathVisits = self.excludedHistory[replacedPath]
            self.excludedHistory.pop(replacedPath)
            replacedPathInEHist = True
        # handle replacing path
        if replacingPath in self.persistentHistory:
            replacingPathVisits = self.persistentHistory[replacingPath]
            if replacedPathVisits > replacingPathVisits:
                self.persistentHistory[replacingPath] = replacedPathVisits
                replacingPathVisitsIncreasedInPHist = True
        elif replacingPath in self.excludedHistory:
            replacingPathVisits = self.excludedHistory[replacingPath]
            if replacedPathVisits > replacingPathVisits:
                self.excludedHistory[replacingPath] = replacedPathVisits
        else: # new path, neither contained in history or favorites (not visited yet, possibly newly created directory)
            if replacedPathInEHist:
                self.excludedHistory[replacingPath] = replacedPathVisits
            else:
                self.persistentHistory[replacingPath] = replacedPathVisits
        # final touch: consolidate history, recompute favorites
        if replacedPathInRHist or replacedPathInPHist or replacingPathVisitsIncreasedInPHist:
            self.__consolidateHistory()
        if replacedPathInEHist:
            self.__computeFavorites()
        return (replacedPath, replacingPath)

    def closeNavigation(self):
        self.__saveNavigationFiles()
        pass

    def __loadNavigationFiles(self):
        nvcdcmn.loadBasicFiles(navset.r_hist_file, navset.r_hist_max_entries, navset.l_hist_file, navset.p_str_hist_file, navset.p_num_hist_file, self.recentHistory, self.dailyLog, self.persistentHistory)
        if os.path.isfile(navset.e_str_hist_file) and os.path.isfile(navset.e_num_hist_file):
            nvcdcmn.readFromPermHist(navset.e_str_hist_file, navset.e_num_hist_file, self.excludedHistory)

    def __saveNavigationFiles(self):
        nvcdcmn.writeBackToTempHist(self.recentHistory, navset.r_hist_file, self.dailyLog, navset.log_dir, navset.l_hist_file)
        nvcdcmn.writeBackToPermHist(self.persistentHistory, navset.p_str_hist_file, navset.p_num_hist_file)
        nvcdcmn.writeBackToPermHist(self.excludedHistory, navset.e_str_hist_file, navset.e_num_hist_file)

    def __doHistoryCleanup(self):
        pHistCleanedUp = 0
        rHistCleanedUp = 0
        # clean up persistent history (except the most visited paths)
        if len(self.persistentHistory) > navset.p_hist_max_entries:
            persistentHistorySortedPaths = []
            for path, visitsCount in sorted(self.persistentHistory.items(), key = lambda k:(k[1], k[0].lower()), reverse = True):
                persistentHistorySortedPaths.append(path)
            for index in range(navset.p_hist_max_entries, len(persistentHistorySortedPaths)):
                currentPath = persistentHistorySortedPaths[index]
                if not os.path.exists(currentPath):
                    del self.persistentHistory[currentPath]
                    pHistCleanedUp += 1
        # clean up recent history
        for path in self.recentHistory:
            if not os.path.exists(path):
                self.recentHistory.remove(path)
                rHistCleanedUp += 1
        #print("Cleaned up persistent history entries: " + str(pHistCleanedUp))
        #print("Cleaned up recent history entries: " + str(rHistCleanedUp))

    def __consolidateHistory(self):
        pHistDict = {}
        limit = 0
        for path, visitsCount in sorted(self.persistentHistory.items(), key = lambda k:(k[1], k[0].lower()), reverse = True):
            if (limit == navset.p_hist_max_entries):
                break
            pHistDict[path] = os.path.basename(path)
            limit += 1
        self.consolidatedHistory = self.recentHistory.copy()
        for path, visitsCount in sorted(pHistDict.items(), key = lambda k:(k[1].lower(), k[0].lower())):
            self.consolidatedHistory.append(path)

    def __computeFavorites(self):
        favDict = {}
        for path in self.excludedHistory.keys():
            favDict[path] = os.path.basename(path)
        self.favorites.clear()
        for path, dirName in sorted(favDict.items(), key = lambda k:(k[1].lower(), k[0].lower())):
            self.favorites.append(path)

""" navigation helper functions """
def getReplacingDirPath(replacingDir):
    replacingDirPath = ":4"
    with open(sysset.input_storage_file, "w") as inputStorage:
        inputStorage.write(replacingDir)
        inputStorage.close() # file needs to be closed otherwise the below executed BASH command might return unexpected results
        # build BASH command for retrieving the absolute path of the replacing dir (if exists)
        command = "input=`head -1 " + sysset.input_storage_file + "`; "
        command = command + "output=" + sysset.output_storage_file + "; "
        command = command + "cd $input 2> /dev/null; if [[ $? == 0  ]]; then pwd > \"$output\"; else echo :4 > \"$output\"; fi"
        os.system(command)
        with open(sysset.output_storage_file, "r") as outputStorage:
            replacingDirPath = outputStorage.readline().strip('\n')
    return replacingDirPath

def retrieveTargetDirPath(gtDirectory):
    # build a command that validates the goto process and helps retrieve the full path of the target directory
    directory = navset.home_dir if len(gtDirectory) == 0 else gtDirectory
    getDir = "directory=`echo " + directory + "`;" #if wildcards are being used the full dir name should be expanded
    cdCommand = "cd " + '\"' + "$directory" + '\"' + " 2> /dev/null;"
    executionStatus = "echo $? > " + sysset.output_storage_file + ";"
    writeTargetDir = "pwd > " + sysset.input_storage_file + ";"
    goToCommand = getDir + "\n" + cdCommand + "\n" + executionStatus + "\n" + writeTargetDir
    # execute command and recover the target directory path
    os.system(goToCommand)
    targetDirPath = ""
    with open(sysset.output_storage_file, "r") as outputStorage:
        if outputStorage.readline().strip('\n') == "0":
            with open(sysset.input_storage_file, "r") as inputStorage:
                targetDirPath = inputStorage.readline().strip('\n')
    return targetDirPath
