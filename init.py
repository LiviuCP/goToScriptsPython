import os, datetime
import consolidate_history as conshist
from os.path import expanduser

def init():
    r_hist_max_entries = 10
    c_r_hist_max_entries = 25
    home_dir = expanduser("~") + "/"
    r_hist_file = home_dir + ".recent_history"
    p_hist_file = home_dir + ".persistent_history"
    e_hist_file = home_dir + ".excluded_history"
    c_r_hist_file = home_dir + ".recent_command_history"
    fav_file = home_dir + ".goto_favorites"
    log_dir = home_dir + ".goToLogs/"
    l_hist_file = log_dir + datetime.datetime.now().strftime("%Y%m%d")

    # ensure all required files exist
    with open(r_hist_file, "a") as r_hist:
        r_hist.write("")
    with open(p_hist_file, "a") as p_hist:
        p_hist.write("")
    with open(e_hist_file, "a") as e_hist:
        e_hist.write("")
    with open(c_r_hist_file, "a") as c_r_hist:
        c_r_hist.write("")
    with open (fav_file, "a") as fav:
        fav.write("")

    # limit the number of entries from recent command and navigation history files to the maximum allowed
    limit_entries_nr(r_hist_file, r_hist_max_entries)
    limit_entries_nr(c_r_hist_file, c_r_hist_max_entries)

    # create the log directory if it does not exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # create the log file for the current day if it does not exist
    with open(l_hist_file, "a") as l_hist:
        l_hist.write("")

    # consolidate history
    conshist.consolidate()

def limit_entries_nr(file_path, max_entries):
    with open(file_path, "r") as f:
        file_content = f.readlines()
        file_entries = 0
        for entry in file_content:
            file_entries = file_entries + 1
    if file_entries > max_entries:
        with open(file_path, "w") as f:
            for entry_nr in range(0, max_entries):
                f.write(file_content[entry_nr])

init()
