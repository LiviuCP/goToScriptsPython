import datetime
from os.path import expanduser

r_hist_max_entries = 10
p_hist_max_entries = 15
max_filtered_hist_entries = 5
home_dir = expanduser("~") + "/"
r_hist_file = home_dir + ".recent_history"
p_str_hist_file = home_dir + ".persistent_history_strings" # actual persistent history paths
p_num_hist_file = home_dir + ".persistent_history_numbers" # number of times each path was visited (each row should match a row from the p_str_hist_file)
e_str_hist_file = home_dir + ".excluded_history_strings" # actual excluded history paths
e_num_hist_file = home_dir + ".excluded_history_numbers" # number of times each path was visited (each row should match a row from the e_str_hist_file)
hist_file = home_dir + ".goto_history"
fav_file = home_dir + ".goto_favorites"
log_dir = home_dir + ".goToLogs/"
l_hist_file = log_dir + datetime.datetime.now().strftime("%Y%m%d")
