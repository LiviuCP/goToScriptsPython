import sys, os, datetime
import common, shared_nav_functions as ns
from os.path import expanduser

r_hist_max_entries = 10
p_hist_max_entries = 15
max_filtered_hist_entries = 5
home_dir = expanduser("~") + "/"
r_hist_file = home_dir + ".recent_history"
p_hist_file = home_dir + ".persistent_history"
e_hist_file = home_dir + ".excluded_history"
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
    with open(r_hist_file, "a") as rHist, open(p_hist_file, "a") as pHist, open(e_hist_file, "a"), open(l_hist_file, "a"), \
         open (fav_file, "a"), open(input_storage_file, "a"), open(output_storage_file, "a"):
        rHist.close() # close, in use by limitEntriesNr()
        common.limitEntriesNr(r_hist_file, r_hist_max_entries) # limit the number of entries from recent navigation history files to the maximum allowed and get unified (recent + persistent) history
        pHist.close() # close, in use by consolidateHistory()
        consolidateHistory()

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
    def canUpdateVisitsInHistoryFile(histFile, updateDict, visitedPath):
        entryContainedInFile = False
        with open(histFile, "r") as hist:
            for entry in hist.readlines():
                splitEntry = entry.strip('\n').split(';')
                path = splitEntry[0]
                if path == visitedPath:
                    updateDict[splitEntry[0]] = int(splitEntry[1]) + 1
                    entryContainedInFile = True
                else:
                    updateDict[splitEntry[0]] = int(splitEntry[1])
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
                    if (canUpdateVisitsInHistoryFile(e_hist_file, eHistUpdateDict, visitedDirPath) == True):
                        with open(e_hist_file, "w") as eHist:
                            for entry in eHistUpdateDict.items():
                                eHist.write(entry[0] + ";" + str(entry[1]) + '\n')
                    else:
                        pHistUpdateDict = {}
                        if not (canUpdateVisitsInHistoryFile(p_hist_file, pHistUpdateDict, visitedDirPath) == True):
                            pHistUpdateDict[visitedDirPath] = 1
                        with open(p_hist_file, "w") as pHist:
                            for entry in sorted(pHistUpdateDict.items(), key = lambda k:(k[1], k[0].lower()), reverse = True):
                                pHist.write(entry[0] + ";" + str(entry[1]) + '\n')

def consolidateHistory():
    with open(r_hist_file, 'r') as rHist, open(p_hist_file, 'r') as pHist, open(hist_file, 'w') as hist:
        rHistDict = {}
        pHistDict = {}
        for entry in rHist.readlines():
            rHistDict[entry.strip('\n')] = os.path.basename(entry.strip('\n'))
        limit = 0
        for entry in pHist.readlines():
            splitEntry = entry.split(";")
            pHistDict[splitEntry[0]] = os.path.basename(splitEntry[0])
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
    with open(p_hist_file, 'r') as pHist:
        result = []
        for entry in pHist.readlines():
            splitEntry = entry.split(";")
            if filterKey.lower() in splitEntry[0].lower():
                result.append(splitEntry[0])
                nrOfMatches = nrOfMatches + 1
        nrOfExposedEntries = nrOfMatches if nrOfMatches < max_filtered_hist_entries else max_filtered_hist_entries
        for index in range(0, nrOfExposedEntries):
            filteredContent.append(result[index])
    return nrOfMatches

def clearHist():
    with open(r_hist_file, "w"), open(p_hist_file, "w"), open(hist_file, "w"), open(l_hist_file, "w"), open(e_hist_file, "w") as eHist, open(fav_file, "r") as fav:
        #re-create excluded history with 0 number of visits for each entry
        for entry in fav.readlines():
            entry = entry.strip('\n')
            eHist.write(entry + ';0\n')

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
    # move entry from persistent (if there) to excluded history
    with open(p_hist_file, "r") as pHist:
        pHistUpdateDict = {}
        movedToExcludedHist = False
        for entry in pHist.readlines():
            splitEntry = entry.strip('\n').split(';')
            path = splitEntry[0]
            if path == pathToAdd:
                with open(e_hist_file, "a") as eHist:
                    eHist.write(path + ";" + str(splitEntry[1]) + "\n")
                    movedToExcludedHist = True
            else:
                pHistUpdateDict[path] = int(splitEntry[1])
        if movedToExcludedHist == True:
            # re-create persistent history file and re-consolidate history
            pHist.close()
            with open(p_hist_file, "w") as pHist:
                for entry in sorted(pHistUpdateDict.items(), key = lambda k:(k[1], k[0].lower()), reverse = True):
                    pHist.write(entry[0] + ";" + str(entry[1]) + '\n')
            consolidateHistory()
        else:
            # add file with no visits to excluded history, it still needs to be there; history remains unchanged
            with open(e_hist_file, "a") as eHist:
                eHist.write(pathToAdd + ";0\n")
        #append path to favorites entries
        with open(fav_file, "a") as fav:
            fav.write(pathToAdd + '\n')
            fav.close() # close, in use by sortFavorites()
            ns.sortFavorites(fav_file)

def removePathFromFavorites(userInput):
    def removeFromExcludedHistory(pathToRemove):
        with open(e_hist_file, "r") as eHist:
            eHistUpdateDict = {}
            pHistUpdateDict = {}
            pathToRemoveVisits = 0
            moveToPersistentHist = False
            for entry in eHist.readlines():
                splitEntry = entry.strip('\n').split(';')
                path = splitEntry[0]
                visits = splitEntry[1]
                if path == pathToRemove:
                    if visits != "0":
                        pathToRemoveVisits = visits
                        moveToPersistentHist = True
                else:
                    eHistUpdateDict[path] = visits
            eHist.close()
            with open(e_hist_file, "w") as eHist:
                for entry in eHistUpdateDict.items():
                    eHist.write(entry[0] + ";" + entry[1] + "\n")
                # move item to persistent history file, re-sort it and re-consolidate history
                if moveToPersistentHist == True:
                    with open(p_hist_file, "r") as pHist:
                        for entry in pHist.readlines():
                            splitEntry = entry.strip('\n').split(';')
                            pHistUpdateDict[splitEntry[0]] = splitEntry[1]
                        pHistUpdateDict[pathToRemove] = pathToRemoveVisits
                        pHist.close()
                        with open(p_hist_file, "w") as pHist:
                            for entry in sorted(pHistUpdateDict.items(), key = lambda k:(k[1], k[0].lower()), reverse = True):
                                pHist.write(entry[0] + ";" + str(entry[1]) + '\n')
                            pHist.close()
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
            removeFromExcludedHistory(pathToRemove)
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
    def removePathFromPermHistoryFile(histFile, pathToRemove):
        itemContainedInHistFile = False
        histContent = []
        with open(histFile, "r") as hist:
            for entry in hist.readlines():
                splitEntry = entry.split(';')
                if splitEntry[0] == pathToRemove:
                    itemContainedInHistFile = True
                else:
                    histContent.append(entry)
            if itemContainedInHistFile == True:
                with open(histFile, "w") as hist:
                    for entry in histContent:
                        hist.write(entry)
        return itemContainedInHistFile
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
        if isInFavFile == True:
            fav.close()
            with open(fav_file, "w") as fav:
                for entry in favContent:
                    fav.write(entry)
            removePathFromPermHistoryFile(e_hist_file, pathToRemove)
        else:
            removedFromPHist = removePathFromPermHistoryFile(p_hist_file, pathToRemove)
        if removedFromRHist == True or removedFromPHist == True:
            consolidateHistory()
    return pathToRemove

def mapMissingDir(pathToReplace, replacingPath):
    def buildHistDict(histDict, histFile):
        with open(histFile, "r") as hist:
            for entry in hist.readlines():
                splitEntry = entry.strip('\n').split(';')
                histDict[splitEntry[0]] = int(splitEntry[1])
    def buildFavContent(favContent):
        with open(fav_file, "r") as fav:
            for entry in fav.readlines():
                favContent.append(entry.strip('\n'))
    def resortAndWriteBackToPersistentHist(pHistDict):
        with open(p_hist_file, "w") as pHist:
            for entry in sorted(pHistDict.items(), key = lambda k:(k[1], k[0].lower()), reverse = True):
                pHist.write(entry[0] + ";" + str(entry[1]) + '\n')
    def writeBackToExcludedHist(eHistDict):
        with open(e_hist_file, "w") as eHist:
            for entry in eHistDict.items():
                eHist.write(entry[0] + ";" + str(entry[1]) + '\n')
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
    buildHistDict(pHistDict, p_hist_file)
    buildHistDict(eHistDict, e_hist_file)
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
        if favBuilt == False:
            buildFavContent(favContent)
            favBuilt = True
        replacingPathVisits = eHistDict[replacingPath]
        if pathToReplaceVisits > replacingPathVisits:
            eHistDict[replacingPath] = pathToReplaceVisits
        if isPathToReplaceInFav:
            favContent.remove(pathToReplace)
    else:
        if isPathToReplaceInFav == True:
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
