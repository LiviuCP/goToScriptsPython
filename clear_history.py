import os, datetime
from os.path import expanduser

def clear_hist():
    home_dir = expanduser("~") + "/"
    log_dir = home_dir + ".goToLogs/"
    r_hist_file = home_dir + ".recent_history"
    p_hist_file = home_dir + ".persistent_history"
    e_hist_file = home_dir + ".excluded_history"
    hist_file = home_dir + ".goto_history"
    fav_file = home_dir + ".goto_favorites"
    l_hist_file = log_dir + datetime.datetime.now().strftime("%Y%m%d")

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

clear_hist()
