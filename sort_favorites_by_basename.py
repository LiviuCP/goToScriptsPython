import os
from os.path import expanduser

def sort_favorites():
    home_dir = expanduser("~") + "/"
    fav_file = fav_file = home_dir + ".goto_favorites"

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

sort_favorites()
