import datetime
from os.path import expanduser

home_dir = expanduser("~") + "/"
c_log_dir = home_dir + ".goToCmdLogs/"

c_hist_file = home_dir + ".command_history"
c_l_hist_file = c_log_dir + datetime.datetime.now().strftime("%Y%m%d")
c_r_hist_file = home_dir + ".recent_command_history"
c_p_str_hist_file = home_dir + ".persistent_command_history_strings" # actual commands
c_p_num_hist_file = home_dir + ".persistent_command_history_numbers" # number of times each command was executed (each row should match a row from the c_p_str_hist_file)

c_r_hist_max_entries = 10
c_p_hist_max_entries = 15
max_filtered_c_hist_entries = 5
min_command_size = 10

sensitive_commands_keywords = {"rmdir ", "rm ", "mv ", "cp "}
