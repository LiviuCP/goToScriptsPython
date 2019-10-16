import os
from os.path import expanduser

def consolidate():
    home_dir = expanduser("~") + "/"
    c_r_hist_file = home_dir + ".recent_command_history"
    c_hist_file = home_dir + ".command_history"

    with open(c_r_hist_file, 'r') as c_r_hist:
        c_r_hist_entries = c_r_hist.readlines()
        c_r_hist_entries.sort()

    with open(c_hist_file, 'w') as c_hist:             # always ensure the file is cleared before (re-)consolidating history
        for entry in c_r_hist_entries:
            c_hist.write(entry)

consolidate()
