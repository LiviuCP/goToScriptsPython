import sys, os, datetime
from os.path import expanduser
import consolidate_history as conshist

home_dir = expanduser("~") + "/"
r_hist_file = home_dir + ".recent_history"
p_hist_file = home_dir + ".persistent_history"
e_hist_file = home_dir + ".excluded_history"
fav_file = home_dir + ".goto_favorites"
l_hist_file = home_dir + ".goToLogs/" + datetime.datetime.now().strftime("%Y%m%d")

def removeDir(path_to_remove):
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
        conshist.consolidate()
    print("")
    print("Entry " + path_to_remove + " has been removed from the menus.")

def removePathFromTempHistoryFile(hist_file, path_to_remove):
    item_contained_in_hist_file = False
    hist_content = []
    with open(hist_file, "r") as hist:
        for entry in hist.readlines():
            if entry.strip('\n') == path_to_remove:
                item_contained_in_hist_file = True
            else:
                hist_content.append(entry)
    if item_contained_in_hist_file == True:
        with open(hist_file, "w") as hist:
            for entry in hist_content:
                hist.write(entry)
    return item_contained_in_hist_file

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
