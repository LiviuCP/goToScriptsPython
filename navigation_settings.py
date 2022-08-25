import datetime
from os.path import expanduser

r_hist_max_entries = 10 # maximum number of paths to be stored in recent navigation history (and displayed in consolidated navigation history)
p_hist_max_entries = 15 # maximum number of entries (paths + visits) to be displayed in consolidated navigation history
max_filtered_hist_entries = 5 # maximum number of paths to be displayed when filtering persistent navigation history
max_filtered_fav_entries = 2 # maximum number of paths to be displayed when filtering favorites
home_dir = expanduser("~") + "/" # user home directory
r_hist_file = home_dir + ".recent_history" # file containing the most recently visited paths
p_str_hist_file = home_dir + ".persistent_history_strings" # file containing the persistent history paths
p_num_hist_file = home_dir + ".persistent_history_numbers" # file containing the number of times each persistent history path was visited
e_str_hist_file = home_dir + ".excluded_history_strings" # file containing the excluded history (favorite) paths
e_num_hist_file = home_dir + ".excluded_history_numbers" # file containing the number of times each excluded history path was visited
hist_file = home_dir + ".goto_history" # consolidated navigation history file
fav_file = home_dir + ".goto_favorites" # navigation favorites file
log_dir = home_dir + ".goToLogs/" # contains all daily log navigation files
l_hist_file = log_dir + datetime.datetime.now().strftime("%Y%m%d") # daily log file, contains all paths visited that day
delayBeforeFinderClose = 0.1 # delay applied before closing Finder via OSAScript
delayBeforeFinderReopen = 0.1 # delay applied before re-opening Finder to prevent any unwanted behavior
delayAfterFinderReopen = 0.9 # delay applied after re-opening Finder to avoid any unwanted behavior
delayErrorFinderReopen = 1.8 # delay applied in case Finder cannot be re-opened due to an error to prevent an early re-open attempt (and a new and maybe more serious error)
