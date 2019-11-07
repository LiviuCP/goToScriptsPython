import os
from os.path import expanduser

def consolidate():
    p_hist_max_entries = 15                            # maximum number of persistent history entries to be displayed in the navigation history menu
    home_dir = expanduser("~") + "/"
    r_hist_file = home_dir + ".recent_history"
    p_hist_file = home_dir + ".persistent_history"
    e_hist_file = home_dir + ".excluded_history"
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
