import datetime
from os.path import expanduser

home_dir = expanduser("~") + "/" # user home directory
c_log_dir = home_dir + ".goToCmdLogs/" # contains daily log commands files

c_hist_file = home_dir + ".command_history" # consolidated commands history file
c_l_hist_file = c_log_dir + datetime.datetime.now().strftime("%Y%m%d") # daily log file, contains all shell commands executed that day
c_r_hist_file = home_dir + ".recent_command_history" # file containing the most recently executed commands
c_p_str_hist_file = home_dir + ".persistent_command_history_strings" # file containing the persistent history commands
c_p_num_hist_file = home_dir + ".persistent_command_history_numbers" # file containing the number of times each shell command was executed

c_r_hist_max_entries = 10 # maximum number of commands to be stored in recent commands history (and displayed in consolidated commands history)
c_p_hist_max_entries = 15 # maximum number of entries (commands + visits) to be displayed in consolidated commands history
max_filtered_c_hist_entries = 5 # maximum number of commands to be displayed when filtering persistent commands history
min_command_size = 10 # minimum number of characters an executed shell command should have to be stored in recent and persistent commands history

sensitive_commands_keywords = {"rmdir ", "rm ", "mv ", "cp "} # commands containing these substrings are treated as sensitive and the user will be prompted to confirm execution in some scenarios
