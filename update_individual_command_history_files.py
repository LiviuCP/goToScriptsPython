import sys, os, datetime
from os.path import expanduser

def update():
    executed_command = sys.argv[1]
    c_r_hist_max_entries = 25
    home_dir = expanduser("~") + "/"
    c_r_hist_file = home_dir + ".recent_command_history"

    with open(c_r_hist_file, "r") as c_r_hist:
        c_r_hist_content = []
        c_r_hist_entries = 0
        for entry in c_r_hist.readlines():
            c_r_hist_content.append(entry.strip('\n'))
            c_r_hist_entries = c_r_hist_entries + 1

    if executed_command in c_r_hist_content:
        c_r_hist_content.remove(executed_command)
    elif c_r_hist_entries == c_r_hist_max_entries:
        c_r_hist_content.remove(c_r_hist_content[c_r_hist_entries-1])
    c_r_hist_content = [executed_command] + c_r_hist_content

    with open(c_r_hist_file, "w") as c_r_hist:
        for entry in c_r_hist_content:
            c_r_hist.write(entry+'\n')

update()
