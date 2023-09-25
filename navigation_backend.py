import sys, os
import nav_cmd_common as nvcdcmn, navigation_settings as navset, system_settings as sysset
from pathlib import Path

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
        self.consolidateHistory()

    def choosePath(self, menuChoice, userInput, filteredContent):
        content = filteredContent if menuChoice in ["-fh", "-ff"] else self.favorites if menuChoice == "-f" else self.consolidatedHistory
        return nvcdcmn.getMenuEntry(userInput, content)

    def isMenuEmpty(self, menuChoice):
        assert menuChoice in ["-h", "-f"], "Invalid menu option argument detected"
        return len(self.favorites if menuChoice == "-f" else self.consolidatedHistory) == 0

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

    def consolidateHistory(self):
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
        nrOfPathVisits = self.persistentHistory.get(pathToAdd)
        if nrOfPathVisits is not None:
            del self.persistentHistory[pathToAdd]
            self.consolidateHistory()
        else:
            nrOfPathVisits = 0
        self.excludedHistory[pathToAdd] = nrOfPathVisits
        self.favorites.append(pathToAdd)
        self.__sortFavorites()

    def removePathFromFavorites(self, userInput):
        pathToRemove = ""
        # remove from favorites, re-sort, remove from excluded history and move to persistent history if visited at least once
        if self.__isValidFavoritesEntryNr(userInput):
            pathToRemove = self.favorites[int(userInput)-1]
            self.favorites.remove(pathToRemove)
            self.__sortFavorites()
            nrOfRemovedPathVisits = self.excludedHistory[pathToRemove]
            if nrOfRemovedPathVisits > 0:
                self.persistentHistory[pathToRemove] = nrOfRemovedPathVisits
                self.consolidateHistory()
        return pathToRemove

    def isContainedInFavorites(self, pathToAdd):
        assert len(pathToAdd) > 0, "Empty path argument detected"
        alreadyAddedToFavorites = False
        for path in self.favorites:
            if path == pathToAdd:
                alreadyAddedToFavorites = True
                break
        return alreadyAddedToFavorites

    def isValidFavoritesEntryNr(self, userInput):
        return self.__isValidFavoritesEntryNr(userInput)

    def isFavEmpty(self):
        return len(self.favorites) == 0

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
        if not removedFromPersistentHistory:
            self.favorites.remove(pathToRemove)
            del self.excludedHistory[pathToRemove]
        if removedFromRecentHistory or removedFromPersistentHistory:
            self.consolidateHistory()
        return pathToRemove

    def mapMissingDir(self, pathToReplace, replacingPath):
        assert len(pathToReplace) > 0, "Empty argument for 'path to replace' detected"
        assert len(replacingPath) > 0, "Empty argument for 'replacing path' detected"
        isPathToReplaceInFav = False
        reSortPHist = False
        reSortFav = False
        # handle path to replace: remove it from all required files
        if pathToReplace in self.dailyLog:
            self.dailyLog.remove(pathToReplace)
        removedFromRHist = False
        if pathToReplace in self.recentHistory:
            self.recentHistory.remove(pathToReplace)
            removedFromRHist = True
        if pathToReplace in self.persistentHistory:
            pathToReplaceVisits = self.persistentHistory[pathToReplace]
            self.persistentHistory.pop(pathToReplace)
        else:
            #only modify the excluded history for the moment, to be removed from favorites in next step
            pathToReplaceVisits = self.excludedHistory[pathToReplace]
            self.excludedHistory.pop(pathToReplace)
            isPathToReplaceInFav = True
        # handle replacing path
        if replacingPath in self.persistentHistory:
            replacingPathVisits = self.persistentHistory[replacingPath]
            if pathToReplaceVisits > replacingPathVisits:
                self.persistentHistory[replacingPath] = pathToReplaceVisits
                reSortPHist = True
            if isPathToReplaceInFav:
                self.favorites.remove(pathToReplace)
        elif replacingPath in self.excludedHistory:
            replacingPathVisits = self.excludedHistory[replacingPath]
            if pathToReplaceVisits > replacingPathVisits:
                self.excludedHistory[replacingPath] = pathToReplaceVisits
            if isPathToReplaceInFav:
                self.favorites.remove(pathToReplace)
        else: # new path, neither contained in history or favorites (not visited yet, possibly newly created directory)
            if isPathToReplaceInFav:
                self.excludedHistory[replacingPath] = pathToReplaceVisits
                self.favorites.remove(pathToReplace)
                self.favorites.append(replacingPath)
                reSortFav = True
            else:
                self.persistentHistory[replacingPath] = pathToReplaceVisits
                reSortPHist = True
        # final touch: re-sort persistent and/or excluded history, consolidate history
        if isPathToReplaceInFav:
            if reSortFav: #old path had been replaced by an unvisited file
                self.__sortFavorites()
                if removedFromRHist:
                    self.consolidateHistory()
            else:
                if replacingPath in self.persistentHistory and reSortPHist: #replacing path is in persistent history and the number of visits had been increased (taken over from the replaced path)
                    self.consolidateHistory()
                elif removedFromRHist:
                    self.consolidateHistory()
        else:
            self.consolidateHistory()
        return (pathToReplace, replacingPath)

    def displayFormattedRecentHistContent(self):
        self.__displayFormattedNavFileContent(self.consolidatedHistory, 0, len(self.recentHistory))

    def displayFormattedPersistentHistContent(self):
        self.__displayFormattedNavFileContent(self.consolidatedHistory, len(self.recentHistory))

    def displayFormattedFilteredContent(self, filteredContent, totalNrOfMatches):
        self.__displayFormattedNavFileContent(filteredContent, 0)
        print("")
        print("\tThe search returned " + str(totalNrOfMatches) + " match(es).")
        if totalNrOfMatches > len(filteredContent):
            print("\tFor better visibility only part of them are displayed. Please narrow the search if needed.")

    def displayFormattedQuickNavigationHistory(self):
        self.__displayFormattedNavFileContent(self.recentHistory, 0, navset.q_hist_max_entries)

    def displayFormattedFavoritesContent(self):
        self.__displayFormattedNavFileContent(self.favorites)

    def closeNavigation(self):
        self.__saveNavigationFiles()
        pass

    def __loadNavigationFiles(self):
        nvcdcmn.loadBasicFiles(navset.r_hist_file, navset.r_hist_max_entries, navset.l_hist_file, navset.p_str_hist_file, navset.p_num_hist_file, self.recentHistory, self.dailyLog, self.persistentHistory)
        if os.path.isfile(navset.e_str_hist_file) and os.path.isfile(navset.e_num_hist_file):
            nvcdcmn.readFromPermHist(navset.e_str_hist_file, navset.e_num_hist_file, self.excludedHistory)
        for path, visitsCount in self.excludedHistory.items():
            self.favorites.append(path)
        self.__sortFavorites()

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

    def __sortFavorites(self):
        favDict = {}
        result = []
        for path in self.favorites:
            favDict[path] = os.path.basename(path)
        for path, visitsCount in sorted(favDict.items(), key = lambda k:(k[1].lower(), k[0].lower())):
            result.append(path)
        self.favorites = result

    def __isValidFavoritesEntryNr(self, userInput):
        isValid = True
        if userInput.isdigit():
            userInput = int(userInput)
            if userInput > len(self.favorites) or userInput == 0:
                isValid = False
        else:
            isValid = False
        return isValid

    def __displayFormattedNavFileContent(self, fileContent, firstRowNr = 0, limit = -1):
        nrOfRows = len(fileContent)
        assert nrOfRows > 0, "Attempt to display an empty navigation menu"
        limit = nrOfRows if limit < 0 or limit > nrOfRows else limit
        assert limit != 0, "Zero entries limit detected, not permitted"
        beginCharsToDisplayForDirName = navset.max_nr_of_item_name_chars // 2 #first characters to be displayed for a directory name exceeding the maximum number of chars to be displayed
        endCharsToDisplayForDirName = beginCharsToDisplayForDirName - navset.max_nr_of_item_name_chars #last characters to be displayed for a directory name exceeding the maximum number of chars to be displayed
        beginCharsToDisplayForPath = navset.max_nr_of_path_chars // 2 #first characters to be displayed for an absolute path exceeding the maximum number of chars to be displayed
        endCharsToDisplayForPath = beginCharsToDisplayForPath - navset.max_nr_of_path_chars #last characters to be displayed for an absolute path exceeding the maximum number of chars to be displayed
        if firstRowNr < limit and firstRowNr >= 0:
            print('{0:<5s} {1:<40s} {2:<40s} {3:<85s}'.format('', '- PARENT DIR -', '- DIR NAME -', '- DIR PATH -'))
            for rowNr in range(firstRowNr, limit):
                dirPath = fileContent[rowNr].strip('\n')
                dirName = os.path.basename(dirPath) if dirPath != "/" else "*root"
                parentDir = os.path.basename(str(Path(dirPath).parent))
                if len(parentDir) == 0:
                    parentDir = "*root"
                elif len(parentDir)-1 > navset.max_nr_of_item_name_chars:
                    parentDir = parentDir[0:beginCharsToDisplayForDirName] + "..." + parentDir[endCharsToDisplayForDirName-1:]
                if len(dirName)-1 > navset.max_nr_of_item_name_chars:
                    dirName = dirName[0:beginCharsToDisplayForDirName] + "..." + dirName[endCharsToDisplayForDirName-1:]
                if len(dirPath)-1 > navset.max_nr_of_path_chars:
                    dirPath = dirPath[0:beginCharsToDisplayForPath] + "..." + dirPath[endCharsToDisplayForPath-1:]
                print('{0:<5s} {1:<40s} {2:<40s} {3:<85s}'.format(str(rowNr+1), parentDir, dirName, dirPath))

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
