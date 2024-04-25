import os
from os.path import expanduser

home_dir = expanduser("~") + "/"
fallback_dir = home_dir #directory used as fallback in case the current directory becomes unavailable (e.g. deleted externally)
input_storage_file = home_dir + ".store_input" #used for communication with the UNIX shell (e.g. BASH), namely for writing input that will be read by the shell
output_storage_file = home_dir + ".store_output" #used for communication with the UNIX shell (e.g. BASH), namely for reading output written by the shell

assert os.path.isdir(fallback_dir), "Invalid fallback directory!"
