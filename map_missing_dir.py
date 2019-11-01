import sys, os, datetime
from os.path import expanduser
import consolidate_history as conshist

home_dir = expanduser("~") + "/"
r_hist_file = home_dir + ".recent_history"
p_hist_file = home_dir + ".persistent_history"
e_hist_file = home_dir + ".excluded_history"
fav_file = home_dir + ".goto_favorites"
l_hist_file = home_dir + ".goToLogs/" + datetime.datetime.now().strftime("%Y%m%d")

# global variables (to be corrected later)
e_hist_dict = {}
p_hist_dict = {}
fav_content = []

def replaceDir(path_to_replace, replacing_path):
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
        buildFavContent()
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
            buildFavContent()
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
        writeBackToExcludedHist()
        if re_sort_fav == True: #old path had been replaced by an unvisited file
            resortAndWriteBackToFav()
            if removed_from_r_hist:
                conshist.consolidate()
        else:
            writeBackToFav() #old path had been removed and taken over by a visited path from persistent history/favorites
            if replacing_path in p_hist_dict and re_sort_p_hist == True: #replacing path is in persistent history and the number of visits had been increased (taken over from the replaced path)
                resortAndWriteBackToPersistentHist()
                conshist.consolidate()
            elif removed_from_r_hist:
                conshist.consolidate()
    else:
        resortAndWriteBackToPersistentHist() #always re-sort persistent history when path to be replaced is there
        if replacing_path in e_hist_dict:
            writeBackToExcludedHist()
        conshist.consolidate()

    # confirm mapping
    print("")
    print("Missing directory " + path_to_replace + " replaced with: " + replacing_path)
    print("")
    print("Mapping performed successfully.")

def buildHistDict(hist_dict, hist_file):
    with open(hist_file, "r") as hist:
        for entry in hist.readlines():
            split_entry = entry.strip('\n').split(';')
            hist_dict[split_entry[0]] = int(split_entry[1])

def buildFavContent():
    with open(fav_file, "r") as fav:
        for entry in fav.readlines():
            fav_content.append(entry.strip('\n'))

def resortAndWriteBackToPersistentHist():
    with open(p_hist_file, "w") as p_hist:
        for entry in sorted(p_hist_dict.items(), key = lambda k:(k[1], k[0].lower()), reverse = True):
            p_hist.write(entry[0] + ";" + str(entry[1]) + '\n')

def writeBackToExcludedHist():
    with open(e_hist_file, "w") as e_hist:
        for entry in e_hist_dict.items():
            e_hist.write(entry[0] + ";" + str(entry[1]) + '\n')

def resortAndWriteBackToFav():
    fav_dict = {}
    for entry in fav_content:
        fav_dict[entry] = os.path.basename(entry)
    with open(fav_file, "w") as fav:
        for entry in sorted(fav_dict.items(), key = lambda k:(k[1].lower(), k[0])):
            fav.write(entry[0] + '\n')

def writeBackToFav():
    with open(fav_file, "w") as fav:
        for entry in fav_content:
            fav.write(entry + '\n')

# duplicate from remove_missing_dir.py, remove later
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
