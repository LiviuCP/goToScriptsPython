from os.path import expanduser

home_dir = expanduser("~") + "/"
input_storage_file = home_dir + ".store_input" #used for communication with the UNIX shell (e.g. BASH), namely for writing input that will be read by the shell
output_storage_file = home_dir + ".store_output" #used for communication with the UNIX shell (e.g. BASH), namely for reading output written by the shell
