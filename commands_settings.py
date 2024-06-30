import datetime
from os.path import expanduser

home_dir = expanduser("~") + "/" # user home directory
log_dir = home_dir + ".goToCmdLogs/" # contains daily log commands files

hist_file = home_dir + ".command_history" # consolidated commands history file
l_hist_file = log_dir + datetime.datetime.now().strftime("%Y%m%d") # daily log file, contains all shell commands executed that day
r_hist_file = home_dir + ".recent_command_history" # file containing the most recently executed commands
p_str_hist_file = home_dir + ".persistent_command_history_strings" # file containing the persistent history commands
p_num_hist_file = home_dir + ".persistent_command_history_numbers" # file containing the number of times each shell command was executed

r_hist_max_entries = 10 # maximum number of commands to be stored in recent commands history (and displayed in consolidated commands history)
p_hist_max_entries = 15 # maximum number of entries (commands + visits) to be displayed in consolidated commands history
q_hist_max_entries = 5 # maximum number of entries to be displayed in the quick commands history
max_filtered_hist_entries = 5 # maximum number of commands to be displayed when filtering persistent commands history
min_command_size = 10 # minimum number of characters an executed shell command should have to be stored in recent and persistent commands history

# commands containing these substrings are treated as sensitive and the user will be prompted to confirm execution in some scenarios
sensitive_commands_keywords = {
    "rmdir ",
    "rm ",
    "mv ",
    "cp ",
    "sudo ",
    "reset ",
    "apply ",
    "checkout ",
    "stash",
    "push",
    "pull",
    "merge"
}
