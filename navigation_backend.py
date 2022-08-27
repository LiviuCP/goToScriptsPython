import sys, os
import common, nav_cmd_common as nvcdcmn, shared_nav_functions as ns, navigation_settings as navset

input_storage_file = navset.home_dir + ".store_input"
output_storage_file = navset.home_dir + ".store_output"

""" navigation history/favorites menu init/access functions """
def initNavMenus():
    # ensure all required files and dirs exist
    if not os.path.exists(navset.log_dir):
        os.makedirs(navset.log_dir)
    with open(navset.r_hist_file, "a") as rHist, open(navset.p_str_hist_file, "a") as pStrHist, open(navset.p_num_hist_file, "a") as pNumHist, open(navset.e_str_hist_file, "a") as eStrHist, open(navset.e_num_hist_file, "a") as eNumHist, \
         open(navset.l_hist_file, "a"), open (navset.fav_file, "a"), open(input_storage_file, "a"), open(output_storage_file, "a"):
        rHist.close() # close, in use by next functions
        pStrHist.close() # close, in use by next functions
        pNumHist.close() # close, in use by next functions
        doHistoryCleanup() #clean all invalid paths from history (except the most visited ones from persistent history)
        nvcdcmn.limitEntriesNr(navset.r_hist_file, navset.r_hist_max_entries) # limit the number of entries from recent navigation history files to the maximum allowed and get unified (recent + persistent) history
        consolidateHistory()

def doHistoryCleanup():
    pHistCleanedUp = 0
    rHistCleanedUp = 0
    with open(navset.p_str_hist_file, "r") as pStrHist, open(navset.p_num_hist_file, "r") as pNumHist, open(navset.r_hist_file, "r") as rHist:
        # clean up persistent history (except the most visited paths)
        pStrHistList = pStrHist.readlines()
        pNumHistList = pNumHist.readlines()
        assert len(pStrHistList) == len(pNumHistList), "The number of elements in p_str_hist_file is different from the number contained in p_num_hist_file"
        pStrHistListUpdated = []
        pNumHistListUpdated = []
        if len(pStrHistList) > navset.p_hist_max_entries:
            pStrHistListUpdated = pStrHistList[0:navset.p_hist_max_entries].copy()
            pNumHistListUpdated = pNumHistList[0:navset.p_hist_max_entries].copy()
            for index in range(navset.p_hist_max_entries, len(pStrHistList)):
                if os.path.exists(pStrHistList[index].strip("\n")):
                    pStrHistListUpdated.append(pStrHistList[index])
                    pNumHistListUpdated.append(pNumHistList[index])
                else:
                    pHistCleanedUp += 1
        # clean up recent history
        rHistEntriesUpdated = []
        for entry in rHist.readlines():
            if os.path.exists(entry.strip('\n')):
                rHistEntriesUpdated.append(entry)
            else:
                rHistCleanedUp += 1
        # write back if entries have been cleaned up
        if pHistCleanedUp > 0:
            pStrHist.close()
            pNumHist.close()
            with open(navset.p_str_hist_file, "w") as pStrHist, open(navset.p_num_hist_file, "w") as pNumHist:
                for index in range(len(pStrHistListUpdated)):
                    pStrHist.write(pStrHistListUpdated[index])
                    pNumHist.write(pNumHistListUpdated[index])
        if rHistCleanedUp > 0:
            rHist.close()
            with open(navset.r_hist_file, "w") as rHist:
                for entry in rHistEntriesUpdated:
                    rHist.write(entry)
    #print("Cleaned up persistent history entries: " + str(pHistCleanedUp))
    #print("Cleaned up recent history entries: " + str(rHistCleanedUp))

def choosePath(menuChoice, userInput, filteredContent):
    result = (":3", "", "")
    if menuChoice in ["-fh", "-ff"]:
        result = nvcdcmn.getMenuEntry(userInput, filteredContent)
    else:
        with open(navset.fav_file if menuChoice == "-f" else navset.hist_file, "r") as fPath:
            result = nvcdcmn.getMenuEntry(userInput, fPath.readlines())
    return result

def displayFormattedRecentHistContent():
    with open(navset.hist_file, "r") as hist, open(navset.r_hist_file, "r") as rHist:
        ns.displayFormattedNavFileContent(hist.readlines(), 0, len(rHist.readlines()))

def displayFormattedPersistentHistContent():
    with open(navset.hist_file, "r") as hist, open(navset.r_hist_file, "r") as rHist:
        ns.displayFormattedNavFileContent(hist.readlines(), len(rHist.readlines()))

def displayFormattedFilteredContent(filteredContent, totalNrOfMatches):
    ns.displayFormattedNavFileContent(filteredContent, 0)
    print("")
    print("\tThe search returned " + str(totalNrOfMatches) + " match(es).")
    if totalNrOfMatches > len(filteredContent):
        print("\tFor better visibility only part of them are displayed. Please narrow the search if needed.")

def isMenuEmpty(menuChoice):
    assert menuChoice in ["-h", "-f"], "Invalid menu option argument detected"
    return os.path.getsize(navset.fav_file if menuChoice == "-f" else navset.hist_file) == 0

""" navigation history update functions """
def updateNavigationHistory(visitedDirPath):
    assert len(visitedDirPath) > 0, "Empty path argument detected"
    nvcdcmn.updateHistory(visitedDirPath, navset.l_hist_file, navset.r_hist_file, navset.r_hist_max_entries, navset.p_str_hist_file, navset.p_num_hist_file, navset.e_str_hist_file, navset.e_num_hist_file)

def consolidateHistory():
    with open(navset.r_hist_file, 'r') as rHist, open(navset.p_str_hist_file, 'r') as pStrHist, open(navset.hist_file, 'w') as hist:
        rHistDict = {}
        pHistDict = {}
        for entry in rHist.readlines():
            rHistDict[entry.strip('\n')] = os.path.basename(entry.strip('\n'))
        limit = 0
        for entry in pStrHist.readlines():
            pHistDict[entry.strip('\n')] = os.path.basename(entry.strip('\n'))
            limit = limit + 1
            if (limit == navset.p_hist_max_entries):
                break
        for entry in sorted(rHistDict.items(), key = lambda k:(k[1].lower(), k[0])):
            hist.write(entry[0] + '\n')
        for entry in sorted(pHistDict.items(), key = lambda k:(k[1].lower(), k[0])):
            hist.write(entry[0] + '\n')

def buildFilteredNavigationHistory(filteredContent, filterKey):
    assert len(filterKey) > 0, "Empty filter key found"
    return nvcdcmn.buildFilteredHistory(filteredContent, filterKey, navset.p_str_hist_file, navset.max_filtered_hist_entries)

def buildFilteredFavorites(filteredContent, filterKey):
    assert len(filterKey) > 0, "Empty filter key found"
    return nvcdcmn.buildFilteredHistory(filteredContent, filterKey, navset.e_str_hist_file, navset.max_filtered_fav_entries)

def clearHistory():
    with open(navset.r_hist_file, "w"), open(navset.p_str_hist_file, "w"), open(navset.p_num_hist_file, "w"), open(navset.hist_file, "w"), open(navset.l_hist_file, "w"), open(navset.e_str_hist_file, "w") as eStrHist, open(navset.e_num_hist_file, "w") as eNumHist, open(navset.fav_file, "r") as fav:
        #re-create excluded history with 0 number of visits for each entry
        for entry in fav.readlines():
            eStrHist.write(entry)
            eNumHist.write('0\n')

""" add/remove from favorites functions """
def isContainedInFavorites(pathToAdd):
    assert len(pathToAdd) > 0, "Empty path argument detected"
    alreadyAddedToFavorites = False
    with open(navset.fav_file, "r") as fav:
        favContent = fav.readlines()
        for entry in favContent:
            if entry.strip('\n') == pathToAdd:
                alreadyAddedToFavorites = True
                break
    return alreadyAddedToFavorites

def addPathToFavorites(pathToAdd):
    assert len(pathToAdd) > 0, "Empty path argument detected"
    nrOfPathVisits = ns.removePathFromPermHistoryFile(navset.p_str_hist_file, navset.p_num_hist_file, pathToAdd)
    with open(navset.e_str_hist_file, "a") as eStrHist, open(navset.e_num_hist_file, "a") as eNumHist, open(navset.fav_file, "a") as fav:
        eStrHist.write(pathToAdd + '\n')
        if nrOfPathVisits is not -1:
            eNumHist.write(str(nrOfPathVisits) + '\n')
            consolidateHistory()
        else:
            eNumHist.write("0\n")
        fav.write(pathToAdd + '\n')
        fav.close() # close, in use by sortFavorites()
        ns.sortFavorites(navset.fav_file)

def removePathFromFavorites(userInput):
    def addToPersistentHistory():
        pHistUpdateDict = {}
        nvcdcmn.readFromPermHist(pHistUpdateDict, navset.p_str_hist_file, navset.p_num_hist_file)
        pHistUpdateDict[pathToRemove] = int(nrOfRemovedPathVisits)
        nvcdcmn.writeBackToPermHist(pHistUpdateDict, navset.p_str_hist_file, navset.p_num_hist_file, True)
        consolidateHistory()
    pathToRemove = ""
    # remove from favorites file, re-sort, remove from excluded history and move to persistent history if visited at least once
    with open(navset.fav_file, "r") as fav:
        favFileContent = fav.readlines()
        pathToRemove = favFileContent[int(userInput)-1]
        favFileContent.remove(pathToRemove)
        fav.close()
        with open(navset.fav_file, "w") as fav:
            for entry in favFileContent:
                fav.write(entry)
            fav.close() # close, in use by sortFavorites()
            ns.sortFavorites(navset.fav_file)
            pathToRemove = pathToRemove.strip('\n')
            nrOfRemovedPathVisits = ns.removePathFromPermHistoryFile(navset.e_str_hist_file, navset.e_num_hist_file, pathToRemove)
            # move to persistent history if at least once visited
            if nrOfRemovedPathVisits > 0:
                addToPersistentHistory()
    return pathToRemove

def isValidInput(userInput):
    isValid = True
    if userInput.isdigit():
        userInput = int(userInput)
        if userInput > common.getNumberOfLines(navset.fav_file) or userInput == 0:
            isValid = False
    else:
        isValid = False
    return isValid

def displayFormattedFavoritesContent():
    with open(navset.fav_file, "r") as fav:
        ns.displayFormattedNavFileContent(fav.readlines())

def isFavEmpty():
    return os.path.getsize(navset.fav_file) == 0

""" missing item removal / mapping from navigation history/favorites menu """
def removeMissingDir(pathToRemove):
    assert len(pathToRemove) > 0, "Empty path argument detected"
    with open(navset.fav_file, "r") as fav:
        ns.removePathFromTempHistoryFile(navset.l_hist_file, pathToRemove)
        removedFromPHist = False
        removedFromRHist = ns.removePathFromTempHistoryFile(navset.r_hist_file, pathToRemove)
        favContent = []
        isInFavFile = False
        for entry in fav.readlines():
            if entry.strip('\n') == pathToRemove:
                isInFavFile = True
            else:
                favContent.append(entry)
        if isInFavFile:
            fav.close()
            with open(navset.fav_file, "w") as fav:
                for entry in favContent:
                    fav.write(entry)
            ns.removePathFromPermHistoryFile(navset.e_str_hist_file, navset.e_num_hist_file, pathToRemove)
        else:
            removedFromPHist = ns.removePathFromPermHistoryFile(navset.p_str_hist_file, navset.p_num_hist_file, pathToRemove) is not -1
        if removedFromRHist or removedFromPHist:
            consolidateHistory()
    return pathToRemove

def mapMissingDir(pathToReplace, replacingPath):
    def buildFavContent(favContent):
        with open(navset.fav_file, "r") as fav:
            for entry in fav.readlines():
                favContent.append(entry.strip('\n'))
    def resortAndWriteBackToFav(favContent):
        favDict = {}
        for entry in favContent:
            favDict[entry] = os.path.basename(entry)
        with open(navset.fav_file, "w") as fav:
            for entry in sorted(favDict.items(), key = lambda k:(k[1].lower(), k[0])):
                fav.write(entry[0] + '\n')
    def writeBackToFav(favContent):
        with open(navset.fav_file, "w") as fav:
            for entry in favContent:
                fav.write(entry + '\n')
    assert len(pathToReplace) > 0, "Empty argument for 'path to replace' detected"
    assert len(replacingPath) > 0, "Empty argument for 'replacing path' detected"
    favContent = []
    pHistDict = {}
    eHistDict = {}
    favBuilt = False
    isPathToReplaceInFav = False
    reSortPHist = False
    reSortFav = False
    # first remove the dir to be replaced from the daily log file if there
    ns.removePathFromTempHistoryFile(navset.l_hist_file, pathToReplace)
    # remove from recent history if there
    removedFromRHist = ns.removePathFromTempHistoryFile(navset.r_hist_file, pathToReplace)
    # handle persistent and excluded history files update
    nvcdcmn.readFromPermHist(pHistDict, navset.p_str_hist_file, navset.p_num_hist_file)
    nvcdcmn.readFromPermHist(eHistDict, navset.e_str_hist_file, navset.e_num_hist_file)
    if pathToReplace in pHistDict:
        pathToReplaceVisits = pHistDict[pathToReplace]
        pHistDict.pop(pathToReplace)
    else:
        #get content of fav file but only modify the excluded history for the moment
        buildFavContent(favContent)
        favBuilt = True
        pathToReplaceVisits = eHistDict[pathToReplace]
        eHistDict.pop(pathToReplace)
        isPathToReplaceInFav = True
    if replacingPath in pHistDict:
        replacingPathVisits = pHistDict[replacingPath]
        if pathToReplaceVisits > replacingPathVisits:
            pHistDict[replacingPath] = pathToReplaceVisits
            reSortPHist = True
        if isPathToReplaceInFav:
            favContent.remove(pathToReplace)
    elif replacingPath in eHistDict:
        if not favBuilt:
            buildFavContent(favContent)
            favBuilt = True
        replacingPathVisits = eHistDict[replacingPath]
        if pathToReplaceVisits > replacingPathVisits:
            eHistDict[replacingPath] = pathToReplaceVisits
        if isPathToReplaceInFav:
            favContent.remove(pathToReplace)
    else:
        if isPathToReplaceInFav:
            eHistDict[replacingPath] = pathToReplaceVisits
            favContent.remove(pathToReplace)
            favContent.append(replacingPath)
            reSortFav = True
        else:
            pHistDict[replacingPath] = pathToReplaceVisits
            reSortPHist = True
    # write back to files
    if isPathToReplaceInFav:
        nvcdcmn.writeBackToPermHist(eHistDict, navset.e_str_hist_file, navset.e_num_hist_file)
        if reSortFav == True: #old path had been replaced by an unvisited file
            resortAndWriteBackToFav(favContent)
            if removedFromRHist:
                consolidateHistory()
        else:
            writeBackToFav(favContent) #old path had been removed and taken over by a visited path from persistent history/favorites
            if replacingPath in pHistDict and reSortPHist == True: #replacing path is in persistent history and the number of visits had been increased (taken over from the replaced path)
                nvcdcmn.writeBackToPermHist(pHistDict, navset.p_str_hist_file, navset.p_num_hist_file, True)
                consolidateHistory()
            elif removedFromRHist:
                consolidateHistory()
    else:
        nvcdcmn.writeBackToPermHist(pHistDict, navset.p_str_hist_file, navset.p_num_hist_file, True) #always re-sort persistent history when path to be replaced is there
        if replacingPath in eHistDict:
            nvcdcmn.writeBackToPermHist(eHistDict, navset.e_str_hist_file, navset.e_num_hist_file)
        consolidateHistory()
    return (pathToReplace, replacingPath)

def getReplacingDirPath(replacingDir):
    replacingDirPath = ":4"
    with open(input_storage_file, "w") as inputStorage:
        inputStorage.write(replacingDir)
        inputStorage.close() # file needs to be closed otherwise the below executed BASH command might return unexpected results
        # build BASH command for retrieving the absolute path of the replacing dir (if exists)
        command = "input=`head -1 " + input_storage_file + "`; "
        command = command + "output=" + output_storage_file + "; "
        command = command + "cd $input 2> /dev/null; if [[ $? == 0  ]]; then pwd > \"$output\"; else echo :4 > \"$output\"; fi"
        os.system(command)
        with open(output_storage_file, "r") as outputStorage:
            replacingDirPath = outputStorage.readline().strip('\n')
    return replacingDirPath

""" Functions related to goto process """
def buildGoToCommand(gtDirectory):
    directory = navset.home_dir if len(gtDirectory) == 0 else gtDirectory
    getDir = "directory=`echo " + directory + "`;" #if wildcards are being used the full dir name should be expanded
    cdCommand = "cd " + '\"' + "$directory" + '\"' + " 2> /dev/null;"
    executionStatus = "echo $? > " + output_storage_file + ";"
    writeCurrentDir = "pwd > " + input_storage_file + ";"
    executeCommandWithStatus = getDir + "\n" + cdCommand + "\n" + executionStatus + "\n" + writeCurrentDir
    return executeCommandWithStatus

def getCurrentDirPath():
    currentDirPath = ""
    with open(output_storage_file, "r") as outputStorage:
        if outputStorage.readline().strip('\n') == "0":
            with open(input_storage_file, "r") as inputStorage:
                currentDirPath = inputStorage.readline().strip('\n')
    return currentDirPath
