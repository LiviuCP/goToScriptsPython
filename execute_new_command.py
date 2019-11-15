import sys, os
from os.path import expanduser
import execute_command as cmd

home_dir = expanduser("~") + "/"
c_r_hist_file = home_dir + ".recent_command_history"
output_storage_file = home_dir + ".store_output"

def executeNew(command = ""):
    if command == "":
        print("No argument provided")
    else:
        cmd.execute(command)
