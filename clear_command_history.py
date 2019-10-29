import os
from os.path import expanduser

def clearHistory():
    home_dir = expanduser("~") + "/"
    c_r_hist_file = home_dir + ".recent_command_history"
    c_hist_file = home_dir + ".command_history"

    #erase all files related to command history
    with open(c_r_hist_file, "w") as c_r_hist:
        c_r_hist.write("")
    with open(c_hist_file, "w") as c_hist:
        c_hist.write("")

    print("Content of command history menu has been erased.")

clearHistory()
