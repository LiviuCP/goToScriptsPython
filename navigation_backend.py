import sys, os, datetime
import common, shared_nav_functions as ns
from os.path import expanduser

r_hist_max_entries = 10
p_hist_max_entries = 15
max_filtered_hist_entries = 5
home_dir = expanduser("~") + "/"
r_hist_file = home_dir + ".recent_history"
p_str_hist_file = home_dir + ".persistent_history_strings" # actual persistent history paths
p_num_hist_file = home_dir + ".persistent_history_numbers" # number of times each path was visited (each row should match a row from the p_str_hist_file)
e_str_hist_file = home_dir + ".excluded_history_strings" # actual excluded history paths
e_num_hist_file = home_dir + ".excluded_history_numbers" # number of times each path was visited (each row should match a row from the e_str_hist_file)
hist_file = home_dir + ".goto_history"
fav_file = home_dir + ".goto_favorites"
log_dir = home_dir + ".goToLogs/"
l_hist_file = log_dir + datetime.datetime.now().strftime("%Y%m%d")
input_storage_file = home_dir + ".store_input"
output_storage_file = home_dir + ".store_output"

""" navigation history/favorites menu init/access functions """
def initNavMenus():
    # ensure all required files and dirs exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    with open(r_hist_file, "a") as rHist, open(p_str_hist_file, "a") as pStrHist, open(p_num_hist_file, "a") as pNumHist, open(e_str_hist_file, "a") as eStrHist, open(e_num_hist_file, "a") as eNumHist, \
         open(l_hist_file, "a"), open (fav_file, "a"), open(input_storage_file, "a"), open(output_storage_file, "a"):
        rHist.close() # close, in use by next functions
        pStrHist.close() # close, in use by next functions
        pNumHist.close() # close, in use by next functions
        doHistoryCleanup() #clean all invalid paths from history (except the most visited ones from persistent history)
        common.limitEntriesNr(r_hist_file, r_hist_max_entries) # limit the number of entries from recent navigation history files to the maximum allowed and get unified (recent + persistent) history
        consolidateHistory()

def doHistoryCleanup():
    pHistCleanedUp = 0
    rHistCleanedUp = 0
    with open(p_str_hist_file, "r") as pStrHist, open(p_num_hist_file, "r") as pNumHist, open(r_hist_file, "r") as rHist:
        # clean up persistent history (except the most visited paths)
        pStrHistList = pStrHist.readlines()
        pNumHistList = pNumHist.readlines()
        assert len(pStrHistList) == len(pNumHistList), "The number of elements in p_str_hist_file is different from the number contained in p_num_hist_file"
        pStrHistListUpdated = []
        pNumHistListUpdated = []
        if len(pStrHistList) > p_hist_max_entries:
            pStrHistListUpdated = pStrHistList[0:p_hist_max_entries].copy()
            pNumHistListUpdated = pNumHistList[0:p_hist_max_entries].copy()
            for index in range(p_hist_max_entries, len(pStrHistList)):
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
            with open(p_str_hist_file, "w") as pStrHist, open(p_num_hist_file, "w") as pNumHist:
                for index in range(len(pStrHistListUpdated)):
                    pStrHist.write(pStrHistListUpdated[index])
                    pNumHist.write(pNumHistListUpdated[index])
        if rHistCleanedUp > 0:
            rHist.close()
            with open(r_hist_file, "w") as rHist:
                for entry in rHistEntriesUpdated:
                    rHist.write(entry)
    #print("Cleaned up persistent history entries: " + str(pHistCleanedUp))
    #print("Cleaned up recent history entries: " + str(rHistCleanedUp))

def choosePath(menuChoice, userInput, filteredContent):
    result = (":3", "", "")
    if menuChoice == "-fh":
        result = common.getMenuEntry(userInput, filteredContent)
    else:
        with open(fav_file if menuChoice == "-f" else hist_file, "r") as fPath:
            result = common.getMenuEntry(userInput, fPath.readlines())
    return result

def displayFormattedRecentHistContent():
    with open(hist_file, "r") as hist, open(r_hist_file, "r") as rHist:
        common.displayFormattedNavFileContent(hist.readlines(), 0, len(rHist.readlines()))

def displayFormattedPersistentHistContent():
    with open(hist_file, "r") as hist, open(r_hist_file, "r") as rHist:
        common.displayFormattedNavFileContent(hist.readlines(), len(rHist.readlines()))

def displayFormattedFilteredHistContent(filteredContent, totalNrOfMatches):
    common.displayFormattedNavFileContent(filteredContent, 0)
    print("")
    print("\tThe search returned " + str(totalNrOfMatches) + " match(es).")
    if totalNrOfMatches > len(filteredContent):
        print("\tFor better visibility only part of them are displayed. Please narrow the search if needed.")

def isMenuEmpty(menuChoice):
    assert menuChoice in ["-h", "-f"], "Invalid menu option argument detected"
    return os.path.getsize(fav_file if menuChoice == "-f" else hist_file) == 0

""" navigation history update functions """
def updateHistory(visitedDirPath):
    def canUpdateVisitsInHistoryFile(strHistFile, numHistFile, updateDict, visitedPath):
        entryContainedInFile = False
        with open(strHistFile, "r") as strHist, open(numHistFile, "r") as numHist:
            strHistList = strHist.readlines()
            numHistList = numHist.readlines()
            assert len(strHistList) == len(numHistList), "The number of elements in the the string history file is different from the number contained in the numbers history file"
            for entryNumber in range(len(strHistList)):
                path = strHistList[entryNumber].strip('\n')
                count = numHistList[entryNumber].strip('\n')
                if path == visitedPath:
                    updateDict[path] = int(count) + 1
                    entryContainedInFile = True
                else:
                    updateDict[path] = int(count)
        return entryContainedInFile
    assert len(visitedDirPath) > 0, "Empty path argument detected"
    with open(l_hist_file, "a") as lHist, open(r_hist_file, "r") as rHist:
        rHistContent = []
        rHistEntries = 0
        for entry in rHist.readlines():
            rHistContent.append(entry.strip('\n'))
            rHistEntries = rHistEntries + 1
        if visitedDirPath in rHistContent:
            rHistContent.remove(visitedDirPath)
        elif rHistEntries == r_hist_max_entries:
            rHistContent.remove(rHistContent[rHistEntries-1])
        rHistContent = [visitedDirPath] + rHistContent
        rHist.close()
        lHist.close()
        with open(r_hist_file, "w") as rHist, open(l_hist_file, "r") as lHist:
            for entry in rHistContent:
                rHist.write(entry+'\n')
            lHistContent = []
            for entry in lHist.readlines():
                lHistContent.append(entry.strip('\n'))
            lHist.close()
            # only update persistent or excluded history file if the visited path is not being contained in the visit log for the current day
            if visitedDirPath not in lHistContent:
                with open(l_hist_file, "a") as lHist:
                    lHist.write(visitedDirPath + "\n")
                    eHistUpdateDict = {}
                    if canUpdateVisitsInHistoryFile(e_str_hist_file, e_num_hist_file, eHistUpdateDict, visitedDirPath):
                        with open(e_str_hist_file, "w") as eStrHist, open(e_num_hist_file, "w") as eNumHist:
                            for path, count in eHistUpdateDict.items():
                                eStrHist.write(path + '\n')
                                eNumHist.write(str(count) + '\n')
                    else:
                        pHistUpdateDict = {}
                        if not canUpdateVisitsInHistoryFile(p_str_hist_file, p_num_hist_file, pHistUpdateDict, visitedDirPath):
                            pHistUpdateDict[visitedDirPath] = 1
                        with open(p_str_hist_file, "w") as pStrHist, open(p_num_hist_file, "w") as pNumHist:
                            for path, count in sorted(pHistUpdateDict.items(), key = lambda k:(k[1], k[0].lower()), reverse = True):
                                pStrHist.write(path + '\n')
                                pNumHist.write(str(count) + '\n')

def consolidateHistory():
    with open(r_hist_file, 'r') as rHist, open(p_str_hist_file, 'r') as pStrHist, open(hist_file, 'w') as hist:
        rHistDict = {}
        pHistDict = {}
        for entry in rHist.readlines():
            rHistDict[entry.strip('\n')] = os.path.basename(entry.strip('\n'))
        limit = 0
        for entry in pStrHist.readlines():
            pHistDict[entry.strip('\n')] = os.path.basename(entry.strip('\n'))
            limit = limit + 1
            if (limit == p_hist_max_entries):
                break
        for entry in sorted(rHistDict.items(), key = lambda k:(k[1].lower(), k[0])):
            hist.write(entry[0] + '\n')
        for entry in sorted(pHistDict.items(), key = lambda k:(k[1].lower(), k[0])):
            hist.write(entry[0] + '\n')

def buildFilteredHistory(filteredContent, filterKey):
    assert len(filterKey) > 0, "Invalid filter key found"
    nrOfMatches = 0
    with open(p_str_hist_file, 'r') as pStrHist:
        result = []
        for entry in pStrHist.readlines():
            if filterKey.lower() in entry.strip('\n').lower():
                result.append(entry.strip('\n'))
                nrOfMatches = nrOfMatches + 1
        nrOfExposedEntries = nrOfMatches if nrOfMatches < max_filtered_hist_entries else max_filtered_hist_entries
        for index in range(nrOfExposedEntries):
            filteredContent.append(result[index])
    return nrOfMatches

def clearHistory():
    with open(r_hist_file, "w"), open(p_str_hist_file, "w"), open(p_num_hist_file, "w"), open(hist_file, "w"), open(l_hist_file, "w"), open(e_str_hist_file, "w") as eStrHist, open(e_num_hist_file, "w") as eNumHist, open(fav_file, "r") as fav:
        #re-create excluded history with 0 number of visits for each entry
        for entry in fav.readlines():
            eStrHist.write(entry)
            eNumHist.write('0\n')

""" add/remove from favorites functions """
def isContainedInFavorites(pathToAdd):
    assert len(pathToAdd) > 0, "Empty path argument detected"
    alreadyAddedToFavorites = False
    with open(fav_file, "r") as fav:
        favContent = fav.readlines()
        for entry in favContent:
            if entry.strip('\n') == pathToAdd:
                alreadyAddedToFavorites = True
                break
    return alreadyAddedToFavorites

def addPathToFavorites(pathToAdd):
    assert len(pathToAdd) > 0, "Empty path argument detected"
    nrOfPathVisits = ns.removePathFromPermHistoryFile(p_str_hist_file, p_num_hist_file, pathToAdd)
    with open(e_str_hist_file, "a") as eStrHist, open(e_num_hist_file, "a") as eNumHist, open(fav_file, "a") as fav:
        eStrHist.write(pathToAdd + '\n')
        if nrOfPathVisits is not -1:
            eNumHist.write(str(nrOfPathVisits) + '\n')
            consolidateHistory()
        else:
            eNumHist.write("0\n")
        fav.write(pathToAdd + '\n')
        fav.close() # close, in use by sortFavorites()
        ns.sortFavorites(fav_file)

def removePathFromFavorites(userInput):
    def addToPersistentHistory():
        pHistUpdateDict = {}
        with open(p_str_hist_file, "r") as pStrHist, open(p_num_hist_file, "r") as pNumHist:
            pStrHistList = pStrHist.readlines()
            pNumHistList = pNumHist.readlines()
            assert len(pStrHistList) == len(pNumHistList), "The number of elements in p_str_hist_file is different from the number contained in p_num_hist_file"
            for index in range(len(pStrHistList)):
                pHistUpdateDict[pStrHistList[index].strip('\n')] = pNumHistList[index].strip('\n')
            pHistUpdateDict[pathToRemove] = str(nrOfRemovedPathVisits)
            pStrHist.close()
            pNumHist.close()
            with open(p_str_hist_file, "w") as pStrHist, open(p_num_hist_file, "w") as pNumHist:
                for path, count in sorted(pHistUpdateDict.items(), key = lambda k:(k[1], k[0].lower()), reverse = True):
                    pStrHist.write(path + '\n')
                    pNumHist.write(count + '\n')
                pStrHist.close()
                pNumHist.close()
                consolidateHistory()
    pathToRemove = ""
    # remove from favorites file, re-sort, remove from excluded history and move to persistent history if visited at least once
    with open(fav_file, "r") as fav:
        favFileContent = fav.readlines()
        pathToRemove = favFileContent[int(userInput)-1]
        favFileContent.remove(pathToRemove)
        fav.close()
        with open(fav_file, "w") as fav:
            for entry in favFileContent:
                fav.write(entry)
            fav.close() # close, in use by sortFavorites()
            ns.sortFavorites(fav_file)
            pathToRemove = pathToRemove.strip('\n')
            nrOfRemovedPathVisits = ns.removePathFromPermHistoryFile(e_str_hist_file, e_num_hist_file, pathToRemove)
            # move to persistent history if at least once visited
            if nrOfRemovedPathVisits > 0:
                addToPersistentHistory()
    return pathToRemove

def isValidInput(userInput):
    isValid = True
    if userInput.isdigit():
        userInput = int(userInput)
        if userInput > common.getNumberOfLines(fav_file) or userInput == 0:
            isValid = False
    else:
        isValid = False
    return isValid

def displayFormattedFavoritesContent():
    with open(fav_file, "r") as fav:
        common.displayFormattedNavFileContent(fav.readlines())

def isFavEmpty():
    return os.path.getsize(fav_file) == 0

""" missing item removal / mapping from navigation history/favorites menu """
def removeMissingDir(pathToRemove):
    assert len(pathToRemove) > 0, "Empty path argument detected"
    with open(fav_file, "r") as fav:
        ns.removePathFromTempHistoryFile(l_hist_file, pathToRemove)
        removedFromPHist = False
        removedFromRHist = ns.removePathFromTempHistoryFile(r_hist_file, pathToRemove)
        favContent = []
        isInFavFile = False
        for entry in fav.readlines():
            if entry.strip('\n') == pathToRemove:
                isInFavFile = True
            else:
                favContent.append(entry)
        if isInFavFile:
            fav.close()
            with open(fav_file, "w") as fav:
                for entry in favContent:
                    fav.write(entry)
            ns.removePathFromPermHistoryFile(e_str_hist_file, e_num_hist_file, pathToRemove)
        else:
            removedFromPHist = ns.removePathFromPermHistoryFile(p_str_hist_file, p_num_hist_file, pathToRemove) is not -1
        if removedFromRHist or removedFromPHist:
            consolidateHistory()
    return pathToRemove

def mapMissingDir(pathToReplace, replacingPath):
    def buildHistDict(histDict, strHistFile, numHistFile):
        with open(strHistFile, "r") as strHist, open(numHistFile, "r") as numHist:
            strHistList = strHist.readlines()
            numHistList = numHist.readlines()
            assert len(strHistList) == len(numHistList), "The number of elements in the the string history file is different from the number contained in the numbers history file"
            for index in range(len(strHistList)):
                histDict[strHistList[index].strip('\n')] = int(numHistList[index].strip('\n'))
    def buildFavContent(favContent):
        with open(fav_file, "r") as fav:
            for entry in fav.readlines():
                favContent.append(entry.strip('\n'))
    def resortAndWriteBackToPersistentHist(pHistDict):
        with open(p_str_hist_file, "w") as pStrHist, open(p_num_hist_file, "w") as pNumHist:
            for path, count in sorted(pHistDict.items(), key = lambda k:(k[1], k[0].lower()), reverse = True):
                pStrHist.write(path + '\n')
                pNumHist.write(str(count) + '\n')
    def writeBackToExcludedHist(eHistDict):
        with open(e_str_hist_file, "w") as eStrHist, open(e_num_hist_file, "w") as eNumHist:
            for path, count in eHistDict.items():
                eStrHist.write(path + '\n')
                eNumHist.write(str(count) + '\n')
    def resortAndWriteBackToFav(favContent):
        favDict = {}
        for entry in favContent:
            favDict[entry] = os.path.basename(entry)
        with open(fav_file, "w") as fav:
            for entry in sorted(favDict.items(), key = lambda k:(k[1].lower(), k[0])):
                fav.write(entry[0] + '\n')
    def writeBackToFav(favContent):
        with open(fav_file, "w") as fav:
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
    ns.removePathFromTempHistoryFile(l_hist_file, pathToReplace)
    # remove from recent history if there
    removedFromRHist = ns.removePathFromTempHistoryFile(r_hist_file, pathToReplace)
    # handle persistent and excluded history files update
    buildHistDict(pHistDict, p_str_hist_file, p_num_hist_file)
    buildHistDict(eHistDict, e_str_hist_file, e_num_hist_file)
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
        writeBackToExcludedHist(eHistDict)
        if reSortFav == True: #old path had been replaced by an unvisited file
            resortAndWriteBackToFav(favContent)
            if removedFromRHist:
                consolidateHistory()
        else:
            writeBackToFav(favContent) #old path had been removed and taken over by a visited path from persistent history/favorites
            if replacingPath in pHistDict and reSortPHist == True: #replacing path is in persistent history and the number of visits had been increased (taken over from the replaced path)
                resortAndWriteBackToPersistentHist(pHistDict)
                consolidateHistory()
            elif removedFromRHist:
                consolidateHistory()
    else:
        resortAndWriteBackToPersistentHist(pHistDict) #always re-sort persistent history when path to be replaced is there
        if replacingPath in eHistDict:
            writeBackToExcludedHist(eHistDict)
        consolidateHistory()
    return (pathToReplace, replacingPath)
