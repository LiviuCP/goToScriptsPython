from os.path import expanduser

home_dir = expanduser("~") + "/" # user home directory

hist_file = home_dir + ".commands_history.json" # unified commands history file
aliases_file = home_dir + ".aliases.json" # file containing user-defined aliases for shell commands

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
