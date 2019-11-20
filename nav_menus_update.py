import sys, os, datetime
import common
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

    # create the log directory if it does not exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # create the log file for the current day if it does not exist
    with open(l_hist_file, "a") as l_hist:
        l_hist.write("")

    # consolidate history
    consolidateHistory()

# 2) Choose path from history or favorites menu

# The result returned by this method is stored into the .store_output file to be picked by the BASH script
# It can have following values: an absolute path or a specific code that indicates a certain behavior:
# :1 - user input stored in .store_input, to be picked and forwarded by BASH
# :2 - user exited the choose path dialog, no further actions
# :3 - invalid or missing first argument sys.argv[1] (not used anymore)
# :4 - empty history or favorites file
def choosePath(file_choice, user_input = ""):
    if file_choice == "":
        print("no menu selected")
        outcome = ":3"
    else:
        already_provided_input = True if user_input != "" else False
        if file_choice == "-f": #favorites
            outcome = chooseEntryFromFavoritesMenu(already_provided_input, user_input).strip('\n')
        elif file_choice == "-h": #consolidated history
            outcome = chooseEntryFromHistoryMenu(already_provided_input, user_input).strip('\n')
        else:
            print("invalid argument provided")
            outcome = ":3"
    return outcome

def chooseEntryFromHistoryMenu(already_provided_input, provided_input):
    with open(hist_file, "r") as hist:
        hist_content = hist.readlines()
    if already_provided_input == False:
        os.system("clear")
        if len(hist_content) == 0:
            print("There are no entries in the history menu.")
            user_input = ""
        else:
            with open(r_hist_file, "r") as r_hist:
                r_hist_entries = len(r_hist.readlines())
            line_nr = 1
            print("NAVIGATION HISTORY")
            print("")
            print("-- RECENTLY VISITED DIRECTORIES --")
            print("")
            while line_nr <= r_hist_entries:
                entry = hist_content[line_nr-1].strip('\n')
                print('{0:<10s} {1:<30s} {2:<160s}'.format(str(line_nr), os.path.basename(entry), entry))
                line_nr = line_nr + 1
            print("")
            print("--  MOST VISITED DIRECTORIES --")
            print("")
            while line_nr <= len(hist_content):
                entry = hist_content[line_nr-1].strip('\n')
                print('{0:<10s} {1:<30s} {2:<160s}'.format(str(line_nr), os.path.basename(entry), entry))
                line_nr = line_nr + 1
            print("")
            print("Current directory: " + os.getcwd())
            print("")
            print("Enter the number of the directory you want to navigate to.")
            print("Enter ! to quit.")
            print("")

            # to update: enable path autocomplete
            user_input = input()
            os.system("clear")
    else:
        user_input = provided_input

    return common.getOutput(user_input, hist_content, "history")

def chooseEntryFromFavoritesMenu(already_provided_input, provided_input):
    with open(fav_file, "r") as fav:
        fav_content = fav.readlines()
    if already_provided_input == False:
        os.system("clear")
        if (len(fav_content) == 0):
            print("There are no entries in the favorites menu.")
            user_input = ""
        else:
            print("FAVORITE DIRECTORIES")
            print("")
            line_nr = 1
            for entry in fav_content:
                entry = entry.strip('\n')
                print('{0:<10s} {1:<30s} {2:<160s}'.format(str(line_nr), os.path.basename(entry), entry))
                line_nr = line_nr + 1
            print("")
            print("Current directory: " + os.getcwd())
            print("")
            print("Enter the number of the directory you want to navigate to.")
            print("Enter ! to quit.")
            print("")

            # to update: enable path autocomplete
            user_input = input()
            os.system("clear")
    else:
        user_input = provided_input

    return common.getOutput(user_input, fav_content, "favorites")

# 3) Update individual navigation history files
def updateHistory(visited_dir_path):
    # Step 0: create log file if not existent
    with open(l_hist_file, "a") as l_hist:
        l_hist.write("")

    # Step 1: update the recent history file
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

    # Step 2: check if the visited directory path is contained in the log file of the current day:
    # - if yes: no more actions required
    # - if not: go to step 3
    with open(l_hist_file, "r") as l_hist:
        l_hist_content = []
        for entry in l_hist.readlines():
            l_hist_content.append(entry.strip('\n'))

    if visited_dir_path not in l_hist_content:
        # Step 3: check if the visited directory path is contained in the persistent history
        # - if yes: update number of visits in the persistent file
        # - if not: go to step 4
        p_hist_update_dict = {}
        if (can_update_visits_in_history_file(p_hist_file, p_hist_update_dict, visited_dir_path) == True):
            with open(p_hist_file, "w") as p_hist:
                for entry in sorted(p_hist_update_dict.items(), key = lambda k:(k[1], k[0].lower()), reverse = True):
                    p_hist.write(entry[0] + ";" + str(entry[1]) + '\n')
        else:
            # Step 4: check if the visited directory path is contained in the excluded history (favorites)
            # - if yes: update number of visits in the excluded file
            # - if not: add it to persistent history
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

# 4) Clear navigation history
def clearHist():
    # clear content of history files (except excluded history) and daily log
    with open(r_hist_file, "w") as r_hist:
        r_hist.write("")
    with open(p_hist_file, "w") as p_hist:
        p_hist.write("")
    with open(hist_file, "w") as hist:
        hist.write("")
    with open(l_hist_file, "w") as l_hist:
        l_hist.write("")

    # reset number of visits in excluded history file
    with open(fav_file, "r") as fav:
        fav_file_content = fav.readlines()
    with open(e_hist_file, "w") as e_hist:
        for entry in fav_file_content:
            entry = entry.strip('\n')
            e_hist.write(entry + ';0\n')

    print("Content of navigation history menu has been erased.")

# 5) Add directory to favorites
def addToFavorites(dirPath = ""):
    path_to_add = getDirPath(dirPath)

    if path_to_add != "":
        added_to_favorites = False

        #add file to favorites if not already there
        already_added_to_favorites = False
        with open(fav_file, "r") as fav:
            fav_content = fav.readlines()
            for entry in fav_content:
                if entry.strip('\n') == path_to_add:
                    already_added_to_favorites = True
                    break

        if already_added_to_favorites == False:
            #move entry from persistent history (if there) to excluded history
            excludeFromPersistentHistory(path_to_add)
            #append path to favorites entries
            with open(fav_file, "a") as fav:
                fav.write(path_to_add + '\n')
            added_to_favorites = True
            sortFavorites()
            print("Directory " + path_to_add + " added to favorites.")
        else:
            print("Directory " + path_to_add + " already added to favorites.")

# converts the dirPath into a usable absolute path (if possible); code :4 is being used for an invalid (or inaccessible) path (similar to other .py files where this code is used)
def getDirPath(dirPath):
    if dirPath == "":
        path_to_add = os.getcwd()
    else:
        path_to_add = dirPath
        with open(input_storage_file, "w") as input_storage:
            input_storage.write(path_to_add)

        # build BASH command for retrieving the absolute path of the replacing dir (if exists)
        command = "input=`head -1 " + input_storage_file + "`; "
        command = command + "output=" + output_storage_file + "; "
        command = command + "cd $input 2> /dev/null; if [[ $? == 0  ]]; then pwd > \"$output\"; else echo :4 > \"$output\"; fi"
        os.system(command)

        with open(output_storage_file, "r") as output_storage:
            path  = output_storage.readline().strip('\n')
        if path == ":4":
            os.system("clear")
            print("Directory " + path_to_add + " does not exist, has been deleted or you might not have the required access level.")
            print("Cannot add to favorites.")
            path_to_add = ""
        else:
            path_to_add = path

    return path_to_add

def excludeFromPersistentHistory(path_to_add):
    p_hist_update_dict = {}
    moved_to_excluded_hist = False
    # move entry from persistent (if there) to excluded history
    with open(p_hist_file, "r") as p_hist:
        for entry in p_hist.readlines():
            split_entry = entry.strip('\n').split(';')
            path = split_entry[0]
            if path == path_to_add:
                with open(e_hist_file, "a") as e_hist:
                    e_hist.write(path + ";" + str(split_entry[1]) + "\n")
                moved_to_excluded_hist = True
            else:
                p_hist_update_dict[path] = int(split_entry[1])
    if moved_to_excluded_hist == True:
        # re-create persistent history file and re-consolidate history
        with open(p_hist_file, "w") as p_hist:
            for entry in sorted(p_hist_update_dict.items(), key = lambda k:(k[1], k[0].lower()), reverse = True):
                p_hist.write(entry[0] + ";" + str(entry[1]) + '\n')
        consolidateHistory()
    else:
        # add file with no visits to excluded history, it still needs to be there; history remains unchanged
        with open(e_hist_file, "a") as e_hist:
            e_hist.write(path_to_add + ";0\n")

# 6) Remove directory from favorites

# as a temporary measure (until the whole script is being migrated to Python) exit codes will be used for more advanced communication with the BASH script
# in this case: 1 - fav file issues, 2 - input is not convenient for the python script (either non-numeric or not within range of entries), BASH will handle it as "normal" input (path to go to)

def removeFromFavorites():
    status = 0 # default status, successful removal or aborted by user
    if not os.path.isfile(fav_file):
        print("The favorites file " + fav_file + " does not exist or has been deleted.")
        status = 1
    elif os.path.getsize(fav_file) == 0:
        print("The favorites file " + fav_file + " is empty!")
        status = 1
    else:
        displayFavoritesEntryRemovalDialog()
        user_input = input()
        os.system("clear")
        if isValidInput(user_input):
            user_input = int(user_input)
            # remove entry from favorites and re-sort
            with open(fav_file, "r") as fav:
                fav_file_content = fav.readlines()
                path_to_remove = fav_file_content[user_input-1]
                fav_file_content.remove(path_to_remove)
            with open(fav_file, "w") as fav:
                for entry in fav_file_content:
                    fav.write(entry)
            sortFavorites()
            # remove entry from excluded history and move it to persistent history if visited at least once
            path_to_remove = path_to_remove.strip('\n')
            removeFromExcludedHistory(path_to_remove)
            print("Entry " + path_to_remove + " removed from favorites menu.")
        elif user_input == '!':
            print("No entry removed from favorites menu.")
        else:
            # input to be forwarded for further handling to BASH
            with open(input_storage_file, "w") as input_storage:
                input_storage.write(user_input)
            status = 2
    return status

def removeFromExcludedHistory(path_to_remove):
    e_hist_update_dict = {}
    p_hist_update_dict = {}
    path_to_remove_visits = 0

    move_to_persistent_hist = False
    # remove entry from excluded history
    with open(e_hist_file, "r") as e_hist:
        for entry in e_hist.readlines():
            split_entry = entry.strip('\n').split(';')
            path = split_entry[0]
            visits = split_entry[1]
            if path == path_to_remove:
                if visits != "0":
                    path_to_remove_visits = visits
                    move_to_persistent_hist = True
            else:
                e_hist_update_dict[path] = visits
    with open(e_hist_file, "w") as e_hist:
        for entry in e_hist_update_dict.items():
            e_hist.write(entry[0] + ";" + entry[1] + "\n")
    # move item to persistent history file, re-sort it and re-consolidate history
    if move_to_persistent_hist == True:
        with open(p_hist_file, "r") as p_hist:
            for entry in p_hist.readlines():
                split_entry = entry.strip('\n').split(';')
                p_hist_update_dict[split_entry[0]] = split_entry[1]
            p_hist_update_dict[path_to_remove] = path_to_remove_visits
        with open(p_hist_file, "w") as p_hist:
            for entry in sorted(p_hist_update_dict.items(), key = lambda k:(k[1], k[0].lower()), reverse = True):
                p_hist.write(entry[0] + ";" + str(entry[1]) + '\n')
        consolidateHistory()

def displayFavoritesContent():
    with open(fav_file, "r") as fav:
        fav_file_content = fav.readlines()
        line_nr = 1
        for entry in fav_file_content:
            entry = entry.strip('\n')
            print('{0:<10s} {1:<30s} {2:<160s}'.format(str(line_nr), os.path.basename(entry), entry))
            line_nr = line_nr + 1

def isValidInput(user_input):
    is_valid = True
    if user_input.isdigit():
        int_input = int(user_input)
        if int_input > getNumberOfLines() or int_input == 0:
            is_valid = False
    else:
        is_valid = False
    return is_valid

def displayFavoritesEntryRemovalDialog():
    print("REMOVE DIRECTORY FROM FAVORITES")
    print('')
    displayFavoritesContent()
    print('')
    print("Current directory: " + os.getcwd())
    print('')
    print("Enter the number of the directory to be removed from favorites.")
    print("Enter ! to quit this dialog.")
    print('')

def getNumberOfLines():
    nr_lines = 0
    with open(fav_file, "r") as fav:
        fav_file_content = fav.readlines()
        for entry in fav_file_content:
            nr_lines = nr_lines + 1
    return nr_lines

# 7) Sort favorites by basename
def sortFavorites():
    # ensure the favorites file exists and create sorting dictionary
    with open(fav_file, "a") as fav:
        fav_dict = {}

    # read data
    with open(fav_file, "r") as fav:
        fav_file_content = fav.readlines()
        for entry in fav_file_content:
            entry = entry.strip('\n')
            fav_dict[entry] = os.path.basename(entry)

    # sort
    with open(fav_file, "w") as fav:
        for entry in sorted(fav_dict.items(), key = lambda k:(k[1].lower(), k[0])):
            fav.write(entry[0] + '\n')

# 8) Remove missing directory from history/favorites
def removeMissingDir(path_to_remove):
    removed_from_p_hist = False
    # first remove it from the daily log file if there
    with open(l_hist_file, "a") as l_hist:
        l_hist.write("")
    removePathFromTempHistoryFile(l_hist_file, path_to_remove)
    # remove from recent history if there
    removed_from_r_hist = removePathFromTempHistoryFile(r_hist_file, path_to_remove)
    # check if directory is contained in favorites
    # - if yes: remove it from favorites file and excluded history
    # - if not: remove it from persistent history
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

# 9) Map missing directory in history/favorites
def mapMissingDir(path_to_replace, replacing_path):
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
    removePathFromTempHistoryFile(l_hist_file, path_to_replace)

    # remove from recent history if there
    removed_from_r_hist = removePathFromTempHistoryFile(r_hist_file, path_to_replace)

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

    # confirm mapping
    os.system("clear")
    print("Missing directory: " + path_to_replace)
    print("Replacing directory: "+ replacing_path)
    print("")
    print("Mapping performed successfully.")

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


# 10) Consolidate navigation history
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

# 11) Shared functions
def removePathFromTempHistoryFile(hist_file, path):
    item_contained_in_hist_file = False
    hist_content = []
    with open(hist_file, "r") as hist:
        for entry in hist.readlines():
            if entry.strip('\n') == path:
                item_contained_in_hist_file = True
            else:
                hist_content.append(entry)
    if item_contained_in_hist_file == True:
        with open(hist_file, "w") as hist:
            for entry in hist_content:
                hist.write(entry)
    return item_contained_in_hist_file
