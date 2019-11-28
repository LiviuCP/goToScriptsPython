import sys, os, datetime
import common, nav_shared as ns
from os.path import expanduser

r_hist_max_entries = 10
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
    with open(r_hist_file, "a") as r_hist:
        r_hist.write("")
    with open(p_hist_file, "a") as p_hist:
        p_hist.write("")
    with open(e_hist_file, "a") as e_hist:
        e_hist.write("")
    with open (fav_file, "a") as fav:
        fav.write("")
    with open(input_storage_file, "a") as input_storage:
        input_storage.write("")
    with open(output_storage_file, "a") as output_storage:
        output_storage.write("")
    # limit the number of entries from recent command and navigation history files to the maximum allowed
    common.limitEntriesNr(r_hist_file, r_hist_max_entries)
    # create the log directory and/or daily log file if not existing
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    with open(l_hist_file, "a") as l_hist:
        l_hist.write("")
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
    with open(hist_file, "r") as hist, open(r_hist_file, "r") as r_hist:
        common.displayFormattedNavFileContent(hist.readlines(), 0, len(r_hist.readlines()))
def displayFormattedPersistentHistContent():
    with open(hist_file, "r") as hist, open(r_hist_file, "r") as r_hist:
        common.displayFormattedNavFileContent(hist.readlines(), len(r_hist.readlines()))
def isMenuEmpty(menuChoice):
    return os.path.getsize(fav_file if menuChoice == "-f" else hist_file) == 0
# 3) Update individual navigation history files
def updateHistory(visited_dir_path):
    # *** helper functions ***
    def can_update_visits_in_history_file(hist_file, update_dict, visited_path):
        entry_contained_in_file = False
        with open(hist_file, "r") as hist:
            for entry in hist.readlines():
                split_entry = entry.strip('\n').split(';')
                path = split_entry[0]
                if path == visited_path:
                    update_dict[split_entry[0]] = int(split_entry[1]) + 1
                    entry_contained_in_file = True
                else:
                    update_dict[split_entry[0]] = int(split_entry[1])
        return entry_contained_in_file
    # *** actual function ***
    with open(l_hist_file, "a") as l_hist:
        l_hist.write("")
    with open(r_hist_file, "r") as r_hist:
        r_hist_content = []
        r_hist_entries = 0
        for entry in r_hist.readlines():
            r_hist_content.append(entry.strip('\n'))
            r_hist_entries = r_hist_entries + 1
    if visited_dir_path in r_hist_content:
        r_hist_content.remove(visited_dir_path)
    elif r_hist_entries == r_hist_max_entries:
        r_hist_content.remove(r_hist_content[r_hist_entries-1])
    r_hist_content = [visited_dir_path] + r_hist_content
    with open(r_hist_file, "w") as r_hist:
        for entry in r_hist_content:
            r_hist.write(entry+'\n')
    with open(l_hist_file, "r") as l_hist:
        l_hist_content = []
        for entry in l_hist.readlines():
            l_hist_content.append(entry.strip('\n'))
    # only update persistent or excluded history file if the visited path is not being contained in the visit log for the current day
    if visited_dir_path not in l_hist_content:
        p_hist_update_dict = {}
        if (can_update_visits_in_history_file(p_hist_file, p_hist_update_dict, visited_dir_path) == True):
            with open(p_hist_file, "w") as p_hist:
                for entry in sorted(p_hist_update_dict.items(), key = lambda k:(k[1], k[0].lower()), reverse = True):
                    p_hist.write(entry[0] + ";" + str(entry[1]) + '\n')
        else:
            e_hist_update_dict = {}

            if (can_update_visits_in_history_file(e_hist_file, e_hist_update_dict, visited_dir_path) == True):
                with open(e_hist_file, "w") as e_hist:
                    for entry in e_hist_update_dict.items():
                        e_hist.write(entry[0] + ";" + str(entry[1]) + '\n')
            else:
                p_hist_update_dict[visited_dir_path] = 1
                with open(p_hist_file, "w") as p_hist:
                    for entry in sorted(p_hist_update_dict.items(), key = lambda k:(k[1], k[0].lower()), reverse = True):
                        p_hist.write(entry[0] + ";" + str(entry[1]) + '\n')
        # update log file for the current day
        with open(l_hist_file, "a") as l_hist:
            l_hist.write(visited_dir_path + "\n")

# 4) Clear navigation history
def clearHist():
    with open(r_hist_file, "w") as r_hist:
        r_hist.write("")
    with open(p_hist_file, "w") as p_hist:
        p_hist.write("")
    with open(hist_file, "w") as hist:
        hist.write("")
    with open(l_hist_file, "w") as l_hist:
        l_hist.write("")
    # only reset number of visits in excluded history file (entries should remain as the favorites menu should NOT be cleared)
    with open(fav_file, "r") as fav:
        fav_file_content = fav.readlines()
    with open(e_hist_file, "w") as e_hist:
        for entry in fav_file_content:
            entry = entry.strip('\n')
            e_hist.write(entry + ';0\n')

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
def removeMissingDir(path_to_remove):
    # *** helper functions ***
    def removePathFromPermHistoryFile(hist_file, path_to_remove):
        item_contained_in_hist_file = False
        hist_content = []
        with open(hist_file, "r") as hist:
            for entry in hist.readlines():
                split_entry = entry.split(';')
                if split_entry[0] == path_to_remove:
                    item_contained_in_hist_file = True
                else:
                    hist_content.append(entry)
        if item_contained_in_hist_file == True:
            with open(hist_file, "w") as hist:
                for entry in hist_content:
                    hist.write(entry)
    # *** actual function ***
    removed_from_p_hist = False
    # first remove it from the daily log file if there
    with open(l_hist_file, "a") as l_hist:
        l_hist.write("")
    ns.removePathFromTempHistoryFile(l_hist_file, path_to_remove)
    # remove from recent history if there
    removed_from_r_hist = ns.removePathFromTempHistoryFile(r_hist_file, path_to_remove)
    # remove the path from favorites file and excluded history OR from persistent history
    fav_content = []
    is_in_fav_file = False
    with open(fav_file, "r") as fav:
        for entry in fav.readlines():
            if entry.strip('\n') == path_to_remove:
                is_in_fav_file = True
            else:
                fav_content.append(entry)
    if is_in_fav_file == True:
        with open(fav_file, "w") as fav:
            for entry in fav_content:
                fav.write(entry)
        removePathFromPermHistoryFile(e_hist_file, path_to_remove)
    else:
        removed_from_p_hist = removePathFromPermHistoryFile(p_hist_file, path_to_remove)
    # consolidate history only if modified
    if removed_from_r_hist == True or removed_from_p_hist == True:
        consolidateHistory()
    os.system("clear")
    print("Entry " + path_to_remove + " has been removed from the menus.")

# 8) Map missing directory in history/favorites
def mapMissingDir(path_to_replace, replacing_path):
    # *** helper functions ***
    def buildHistDict(hist_dict, hist_file):
        with open(hist_file, "r") as hist:
            for entry in hist.readlines():
                split_entry = entry.strip('\n').split(';')
                hist_dict[split_entry[0]] = int(split_entry[1])
    def buildFavContent(fav_content):
        with open(fav_file, "r") as fav:
            for entry in fav.readlines():
                fav_content.append(entry.strip('\n'))
    def resortAndWriteBackToPersistentHist(p_hist_dict):
        with open(p_hist_file, "w") as p_hist:
            for entry in sorted(p_hist_dict.items(), key = lambda k:(k[1], k[0].lower()), reverse = True):
                p_hist.write(entry[0] + ";" + str(entry[1]) + '\n')
    def writeBackToExcludedHist(e_hist_dict):
        with open(e_hist_file, "w") as e_hist:
            for entry in e_hist_dict.items():
                e_hist.write(entry[0] + ";" + str(entry[1]) + '\n')
    def resortAndWriteBackToFav(fav_content):
        fav_dict = {}
        for entry in fav_content:
            fav_dict[entry] = os.path.basename(entry)
        with open(fav_file, "w") as fav:
            for entry in sorted(fav_dict.items(), key = lambda k:(k[1].lower(), k[0])):
                fav.write(entry[0] + '\n')
    def writeBackToFav(fav_content):
        with open(fav_file, "w") as fav:
            for entry in fav_content:
                fav.write(entry + '\n')
    # *** actual function ***
    fav_content = []
    p_hist_dict = {}
    e_hist_dict = {}
    fav_built = False
    is_path_to_replace_in_fav = False
    re_sort_p_hist = False
    re_sort_fav = False
    # first remove the dir to be replaced from the daily log file if there
    with open(l_hist_file, "a") as l_hist:
        l_hist.write("")
    ns.removePathFromTempHistoryFile(l_hist_file, path_to_replace)
    # remove from recent history if there
    removed_from_r_hist = ns.removePathFromTempHistoryFile(r_hist_file, path_to_replace)
    # handle persistent and excluded history files update
    buildHistDict(p_hist_dict, p_hist_file)
    buildHistDict(e_hist_dict, e_hist_file)
    if path_to_replace in p_hist_dict:
        path_to_replace_visits = p_hist_dict[path_to_replace]
        p_hist_dict.pop(path_to_replace)
    else:
        #get content of fav file but only modify the excluded history for the moment
        buildFavContent(fav_content)
        fav_built = True
        path_to_replace_visits = e_hist_dict[path_to_replace]
        e_hist_dict.pop(path_to_replace)
        is_path_to_replace_in_fav = True
    if replacing_path in p_hist_dict:
        replacing_path_visits = p_hist_dict[replacing_path]
        if path_to_replace_visits > replacing_path_visits:
            p_hist_dict[replacing_path] = path_to_replace_visits
            re_sort_p_hist = True
        if is_path_to_replace_in_fav:
            fav_content.remove(path_to_replace)
    elif replacing_path in e_hist_dict:
        if fav_built == False:
            buildFavContent(fav_content)
            fav_built = True
        replacing_path_visits = e_hist_dict[replacing_path]
        if path_to_replace_visits > replacing_path_visits:
            e_hist_dict[replacing_path] = path_to_replace_visits
        if is_path_to_replace_in_fav:
            fav_content.remove(path_to_replace)
    else:
        if is_path_to_replace_in_fav == True:
            e_hist_dict[replacing_path] = path_to_replace_visits
            fav_content.remove(path_to_replace)
            fav_content.append(replacing_path)
            re_sort_fav = True
        else:
            p_hist_dict[replacing_path] = path_to_replace_visits
            re_sort_p_hist = True
    # write back to files
    if is_path_to_replace_in_fav:
        writeBackToExcludedHist(e_hist_dict)
        if re_sort_fav == True: #old path had been replaced by an unvisited file
            resortAndWriteBackToFav(fav_content)
            if removed_from_r_hist:
                consolidateHistory()
        else:
            writeBackToFav(fav_content) #old path had been removed and taken over by a visited path from persistent history/favorites
            if replacing_path in p_hist_dict and re_sort_p_hist == True: #replacing path is in persistent history and the number of visits had been increased (taken over from the replaced path)
                resortAndWriteBackToPersistentHist(p_hist_dict)
                consolidateHistory()
            elif removed_from_r_hist:
                consolidateHistory()
    else:
        resortAndWriteBackToPersistentHist(p_hist_dict) #always re-sort persistent history when path to be replaced is there
        if replacing_path in e_hist_dict:
            writeBackToExcludedHist(e_hist_dict)
        consolidateHistory()
    return (path_to_replace, replacing_path)

# 9) Consolidate navigation menu (persistent and recent history)
def consolidateHistory():
    p_hist_max_entries = 15                            # maximum number of persistent history entries to be displayed in the navigation history menu
    c_hist_file = home_dir + ".goto_history"           # consolidated history file (content displayed in navigation history menu)

    with open(r_hist_file, 'r') as r_hist:
        r_hist_entries = r_hist.readlines()
    with open(p_hist_file, 'r') as p_hist:
        p_hist_entries = p_hist.readlines()
    with open(c_hist_file, 'w') as c_hist:             # always ensure the file is cleared before (re-)consolidating history
        r_hist_dict = {}
        p_hist_dict = {}
    for entry in r_hist_entries:
        r_hist_dict[entry.strip('\n')] = os.path.basename(entry.strip('\n'))
    limit = 0
    for entry in p_hist_entries:
        split_entry = entry.split(";")
        p_hist_dict[split_entry[0]] = os.path.basename(split_entry[0])
        limit = limit + 1
        if (limit == p_hist_max_entries):
            break
    # sort entries by directory name so the user can easily find the dirs in the navigation history
    with open(c_hist_file, 'a') as c_hist:
        for entry in sorted(r_hist_dict.items(), key = lambda k:(k[1].lower(), k[0])):
            c_hist.write(entry[0] + '\n')
        for entry in sorted(p_hist_dict.items(), key = lambda k:(k[1].lower(), k[0])):
            c_hist.write(entry[0] + '\n')
