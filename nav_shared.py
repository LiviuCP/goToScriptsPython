import os

# functions shared within nav_menu_update.py and not used elsewhere

def sortFavorites(fav_file): # to do: handle empty argument
    fav_dict = {}
    with open(fav_file, "r") as fav:
        fav_file_content = fav.readlines()
        for entry in fav_file_content:
            entry = entry.strip('\n')
            fav_dict[entry] = os.path.basename(entry)
    with open(fav_file, "w") as fav:
        for entry in sorted(fav_dict.items(), key = lambda k:(k[1].lower(), k[0])):
            fav.write(entry[0] + '\n')

def removePathFromTempHistoryFile(hist_file, path): # to do: handle empty arguments
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
