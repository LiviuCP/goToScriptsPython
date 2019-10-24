import sys, os
from os.path import expanduser
import consolidate_history as conshist
import sort_favorites_by_basename as sortfav

home_dir = expanduser("~") + "/"
p_hist_file = home_dir + ".persistent_history"
e_hist_file = home_dir + ".excluded_history"
fav_file = home_dir + ".goto_favorites"
input_storage_file = home_dir + ".store_input"

# as a temporary measure (until the whole script is being migrated to Python) exit codes will be used for more advanced communication with the BASH script
# in this case: 1 - fav file issues, 2 - input is not convenient for the python script (either non-numeric or not within range of entries), BASH will handle it as "normal" input (path to go to)

def removeFromFavorites():
    if not os.path.isfile(fav_file):
        print("The favorites file " + fav_file + " does not exist or has been deleted.")
        sys.exit(1)
    elif os.path.getsize(fav_file) == 0:
        print("The favorites file " + fav_file + " is empty!")
        sys.exit(1)
    else:
        displayFavoritesEntryRemovalDialog()
        user_input = input()
        os.system("clear")
        if isValidInput(user_input):
            user_input = int(user_input)
        elif user_input == '!':
            print("No entry removed from favorites menu.")
            exit(0)
        else:
            # input to be forwarded for further handling to BASH
            with open(input_storage_file, "w") as input_storage:
                input_storage.write(user_input)
            exit(2)
        # remove entry from favorites and re-sort
        with open(fav_file, "r") as fav:
            fav_file_content = fav.readlines()
            path_to_remove = fav_file_content[user_input-1]
            fav_file_content.remove(path_to_remove)
        with open(fav_file, "w") as fav:
            for entry in fav_file_content:
                fav.write(entry)
        sortfav.sort_favorites()
        # remove entry from excluded history and move it to persistent history if visited at least once
        path_to_remove = path_to_remove.strip('\n')
        removeFromExcludedHistory(path_to_remove)
        print("Entry " + path_to_remove + " removed from favorites menu.")

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
        conshist.consolidate()

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

removeFromFavorites()
