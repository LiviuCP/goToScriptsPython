import sys, os, datetime
import common, nav_shared as ns
from os.path import expanduser

r_hist_max_entries = 10
p_hist_max_entries = 15
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

# 1) Initialize navigation environment
def initNavMenus():
    # ensure all required files exist
    with open(r_hist_file, "a") as rHist:
        rHist.write("")
    with open(p_hist_file, "a") as pHist:
        pHist.write("")
    with open(e_hist_file, "a") as eHist:
        eHist.write("")
    with open (fav_file, "a") as fav:
        fav.write("")
    with open(input_storage_file, "a") as inputStorage:
        inputStorage.write("")
    with open(output_storage_file, "a") as outputStorage:
        outputStorage.write("")
    # limit the number of entries from recent command and navigation history files to the maximum allowed
    common.limitEntriesNr(r_hist_file, r_hist_max_entries)
    # create the log directory and/or daily log file if not existing
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    with open(l_hist_file, "a") as lHist:
        lHist.write("")
    # get consolidated recent/persistent history menu
    consolidateHistory()

# 2) Choose path from history or favorites menu

# The returned outcome could have following special values in the first field:
# :1 - user input to be forwarded as regular input (path name/command)
# :2 - user exited the history/favorites menu, returned to navigation mode
# :3 - invalid first argument
# :4 - no entries in history/favorites menu
def choosePath(menuChoice, userInput):
    file_path = fav_file if menuChoice == "-f" else hist_file
    menuName = "favorites" if menuChoice == "-f" else "history"
    with open(file_path, "r") as fPath:
        content = fPath.readlines()
    return common.getOutput(userInput, content, menuName)
def displayFormattedRecentHistContent():
    with open(hist_file, "r") as hist, open(r_hist_file, "r") as rHist:
        common.displayFormattedNavFileContent(hist.readlines(), 0, len(rHist.readlines()))
def displayFormattedPersistentHistContent():
    with open(hist_file, "r") as hist, open(r_hist_file, "r") as rHist:
        common.displayFormattedNavFileContent(hist.readlines(), len(rHist.readlines()))
def isMenuEmpty(menuChoice):
    return os.path.getsize(fav_file if menuChoice == "-f" else hist_file) == 0
# 3) Update individual navigation history files
def updateHistory(visitedDirPath):
    # *** helper functions ***
    def canUpdateVisitsInHistoryFile(hist_file, updateDict, visitedPath):
        entryContainedInFile = False
        with open(hist_file, "r") as hist:
            for entry in hist.readlines():
                splitEntry = entry.strip('\n').split(';')
                path = splitEntry[0]
                if path == visitedPath:
                    updateDict[splitEntry[0]] = int(splitEntry[1]) + 1
                    entryContainedInFile = True
                else:
                    updateDict[splitEntry[0]] = int(splitEntry[1])
        return entryContainedInFile
    # *** actual function ***
    with open(l_hist_file, "a") as lHist:
        lHist.write("")
    with open(r_hist_file, "r") as rHist:
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
    with open(r_hist_file, "w") as rHist:
        for entry in rHistContent:
            rHist.write(entry+'\n')
    with open(l_hist_file, "r") as lHist:
        lHistContent = []
        for entry in lHist.readlines():
            lHistContent.append(entry.strip('\n'))
    # only update persistent or excluded history file if the visited path is not being contained in the visit log for the current day
    if visitedDirPath not in lHistContent:
        pHistUpdateDict = {}
        if (canUpdateVisitsInHistoryFile(p_hist_file, pHistUpdateDict, visitedDirPath) == True):
            with open(p_hist_file, "w") as pHist:
                for entry in sorted(pHistUpdateDict.items(), key = lambda k:(k[1], k[0].lower()), reverse = True):
                    pHist.write(entry[0] + ";" + str(entry[1]) + '\n')
        else:
            eHistUpdateDict = {}

            if (canUpdateVisitsInHistoryFile(e_hist_file, eHistUpdateDict, visitedDirPath) == True):
                with open(e_hist_file, "w") as eHist:
                    for entry in eHistUpdateDict.items():
                        eHist.write(entry[0] + ";" + str(entry[1]) + '\n')
            else:
                pHistUpdateDict[visitedDirPath] = 1
                with open(p_hist_file, "w") as pHist:
                    for entry in sorted(pHistUpdateDict.items(), key = lambda k:(k[1], k[0].lower()), reverse = True):
                        pHist.write(entry[0] + ";" + str(entry[1]) + '\n')
        # update log file for the current day
        with open(l_hist_file, "a") as lHist:
            lHist.write(visitedDirPath + "\n")

# 4) Clear navigation history
def clearHist():
    with open(r_hist_file, "w") as rHist:
        rHist.write("")
    with open(p_hist_file, "w") as pHist:
        pHist.write("")
    with open(hist_file, "w") as hist:
        hist.write("")
    with open(l_hist_file, "w") as lHist:
        lHist.write("")
    # only reset number of visits in excluded history file (entries should remain as the favorites menu should NOT be cleared)
    with open(fav_file, "r") as fav:
        favFileContent = fav.readlines()
    with open(e_hist_file, "w") as eHist:
        for entry in favFileContent:
            entry = entry.strip('\n')
            eHist.write(entry + ';0\n')

# 5) Add directory to favorites
def isContainedInFavorites(pathToAdd):
    alreadyAddedToFavorites = False
    with open(fav_file, "r") as fav:
        favContent = fav.readlines()
        for entry in favContent:
            if entry.strip('\n') == pathToAdd:
                alreadyAddedToFavorites = True
                break
    return alreadyAddedToFavorites

def addPathToFavorites(pathToAdd):
    pHistUpdateDict = {}
    movedToExcludedHist = False
    # move entry from persistent (if there) to excluded history
    with open(p_hist_file, "r") as pHist:
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
    ns.sortFavorites(fav_file)

# 6) Remove directory from favorites
def removeFromFavorites(userInput):
    # *** helper functions ***
    def removeFromExcludedHistory(pathToRemove):
        eHistUpdateDict = {}
        pHistUpdateDict = {}
        pathToRemoveVisits = 0
        moveToPersistentHist = False
        # remove entry from excluded history
        with open(e_hist_file, "r") as eHist:
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
            with open(p_hist_file, "w") as pHist:
                for entry in sorted(pHistUpdateDict.items(), key = lambda k:(k[1], k[0].lower()), reverse = True):
                    pHist.write(entry[0] + ";" + str(entry[1]) + '\n')
            consolidateHistory()
    # *** actual function: remove from favorites file, re-sort, remove from excluded history and move to persistent history if visited at least once ***
    with open(fav_file, "r") as fav:
        favFileContent = fav.readlines()
        pathToRemove = favFileContent[int(userInput)-1]
        favFileContent.remove(pathToRemove)
    with open(fav_file, "w") as fav:
        for entry in favFileContent:
            fav.write(entry)
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

# 7) Remove missing directory from history/favorites
def removeMissingDir(pathToRemove):
    # *** helper functions ***
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
    # *** actual function ***
    removedFromPHist = False
    # first remove it from the daily log file if there
    with open(l_hist_file, "a") as lHist:
        lHist.write("")
    ns.removePathFromTempHistoryFile(l_hist_file, pathToRemove)
    # remove from recent history if there
    removedFromRHist = ns.removePathFromTempHistoryFile(r_hist_file, pathToRemove)
    # remove the path from favorites file and excluded history OR from persistent history
    favContent = []
    isInFavFile = False
    with open(fav_file, "r") as fav:
        for entry in fav.readlines():
            if entry.strip('\n') == pathToRemove:
                isInFavFile = True
            else:
                favContent.append(entry)
    if isInFavFile == True:
        with open(fav_file, "w") as fav:
            for entry in favContent:
                fav.write(entry)
        removePathFromPermHistoryFile(e_hist_file, pathToRemove)
    else:
        removedFromPHist = removePathFromPermHistoryFile(p_hist_file, pathToRemove)
    # consolidate history only if modified
    if removedFromRHist == True or removedFromPHist == True:
        consolidateHistory()
    return pathToRemove

# 8) Map missing directory in history/favorites
def mapMissingDir(pathToReplace, replacingPath):
    # *** helper functions ***
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
    # *** actual function ***
    favContent = []
    pHistDict = {}
    eHistDict = {}
    favBuilt = False
    isPathToReplaceInFav = False
    reSortPHist = False
    reSortFav = False
    # first remove the dir to be replaced from the daily log file if there
    with open(l_hist_file, "a") as lHist:
        lHist.write("")
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

# 9) Consolidate navigation menu (persistent and recent history)
def consolidateHistory():
    with open(r_hist_file, 'r') as rHist:
        rHistEntries = rHist.readlines()
    with open(p_hist_file, 'r') as pHist:
        pHistEntries = pHist.readlines()
    with open(hist_file, 'w') as hist:             # always ensure the file is cleared before (re-)consolidating history
        rHistDict = {}
        pHistDict = {}
    for entry in rHistEntries:
        rHistDict[entry.strip('\n')] = os.path.basename(entry.strip('\n'))
    limit = 0
    for entry in pHistEntries:
        splitEntry = entry.split(";")
        pHistDict[splitEntry[0]] = os.path.basename(splitEntry[0])
        limit = limit + 1
        if (limit == p_hist_max_entries):
            break
    # sort entries by directory name so the user can easily find the dirs in the navigation history
    with open(hist_file, 'a') as hist:
        for entry in sorted(rHistDict.items(), key = lambda k:(k[1].lower(), k[0])):
            hist.write(entry[0] + '\n')
        for entry in sorted(pHistDict.items(), key = lambda k:(k[1].lower(), k[0])):
            hist.write(entry[0] + '\n')
