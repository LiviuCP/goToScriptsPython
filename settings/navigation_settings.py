from os.path import expanduser

r_hist_max_entries = 10 # maximum number of paths to be stored in recent navigation history (and displayed in consolidated navigation history)
p_hist_max_entries = 15 # maximum number of entries (paths + visits) to be displayed in consolidated navigation history
q_hist_max_entries = 5 # maximum number of entries to be displayed in the quick navigation history
max_filtered_hist_entries = 5 # maximum number of paths to be displayed when filtering persistent navigation history
max_filtered_fav_entries = 2 # maximum number of paths to be displayed when filtering favorites
home_dir = expanduser("~") + "/" # user home directory
hist_file = home_dir + ".navigation_history.json" # unified navigation history file (without excluded history)
e_hist_file = home_dir + ".excluded_navigation_history.json" # excluded navigation history (favorite directories)
max_nr_of_item_name_chars = 25 # maximum number of characters to display for the file/dir name
max_nr_of_path_chars = 75 # maximum number of characters to display for a path (of a directory)
max_nr_of_displayed_items = 50 # maximum number of files/dirs listed from current directory in navigation mode
