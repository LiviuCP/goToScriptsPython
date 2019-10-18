import sys, os
from os.path import expanduser
import consolidate_history as conshist
import sort_favorites_by_basename as sortfav

home_dir = expanduser("~") + "/"
p_hist_file = home_dir + ".persistent_history"
e_hist_file = home_dir + ".excluded_history"
fav_file = home_dir + ".goto_favorites"

# it is assumed that a correct absolute path is provided by calling script as first argument (to be corrected later)
path_to_add = sys.argv[1]

def addToFavorites():
    added_to_favorites = False

    #ensure the favorites file exists
    with open(fav_file, "a") as fav:
        fav.write("")

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
        excludeFromPersistentHistory()
        #append path to favorites entries
        with open(fav_file, "a") as fav:
            fav.write(path_to_add + '\n')
        added_to_favorites = True
        sortfav.sort_favorites()
        print("Directory " + path_to_add + " added to favorites.")
    else:
        print("Directory " + path_to_add + " already added to favorites.")

def excludeFromPersistentHistory():
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
        conshist.consolidate()
    else:
        # add file with no visits to excluded history, it still needs to be there; history remains unchanged
        with open(e_hist_file, "a") as e_hist:
            e_hist.write(path_to_add + ";0\n")

addToFavorites()
