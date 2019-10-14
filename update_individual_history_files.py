import sys, os, datetime
from os.path import expanduser

def update():
    visited_dir_path = sys.argv[1]
    r_hist_max_entries = 10
    home_dir = expanduser("~") + "/"
    r_hist_file = home_dir + ".recent_history"
    p_hist_file = home_dir + ".persistent_history"
    e_hist_file = home_dir + ".excluded_history"
    l_hist_file = home_dir + ".goToLogs/" + datetime.datetime.now().strftime("%Y%m%d")

    # Step 1: update the recent history file
    with open(r_hist_file, "r") as r_hist:
        r_hist_content = []
        r_hist_entries = 0
        for entry in r_hist.readlines():
            r_hist_content.append(entry.strip('\n'))
            r_hist_entries = r_hist_entries + 1

    if visited_dir_path in r_hist_content:
        r_hist_content.remove(visited_dir_path)
    elif r_hist_entries == r_hist_max_entries:
        r_hist_content.remove(r_hist_content[r_hist_entries-1])
    r_hist_content = [visited_dir_path] + r_hist_content

    with open(r_hist_file, "w") as r_hist:
        for entry in r_hist_content:
            r_hist.write(entry+'\n')

    # Step 2: check if the visited directory path is contained in the log file of the current day:
    # - if yes: no more actions required
    # - if not: go to step 3
    with open(l_hist_file, "r") as l_hist:
        l_hist_content = []
        for entry in l_hist.readlines():
            l_hist_content.append(entry.strip('\n'))

    if visited_dir_path not in l_hist_content:
        # Step 3: check if the visited directory path is contained in the persistent history
        # - if yes: update number of visits in the persistent file
        # - if not: go to step 4
        p_hist_update_dict = {}
        if (can_update_visits_in_history_file(p_hist_file, p_hist_update_dict, visited_dir_path) == True):
            with open(p_hist_file, "w") as p_hist:
                for entry in sorted(p_hist_update_dict.items(), key = lambda k:(k[1], k[0].lower()), reverse = True):
                    p_hist.write(entry[0] + ";" + str(entry[1]) + '\n')
        else:
            # Step 4: check if the visited directory path is contained in the excluded history (favorites)
            # - if yes: update number of visits in the excluded file
            # - if not: add it to persistent history
            e_hist_update_dict = {}

            if (can_update_visits_in_history_file(e_hist_file, e_hist_update_dict, visited_dir_path) == True):
                with open(e_hist_file, "w") as e_hist:
                    for entry in e_hist_update_dict.items():
                        e_hist.write(entry[0] + ";" + str(entry[1]) + '\n')
            else:
                p_hist_update_dict[visited_dir_path] = 1
                with open(p_hist_file, "w") as p_hist:
                    for entry in sorted(p_hist_update_dict.items(), key = lambda k:(k[1], k[0].lower()), reverse = True):
                        p_hist.write(entry[0] + ";" + str(entry[1]) + '\n')
        # update log file for the current day
        with open(l_hist_file, "a") as l_hist:
            l_hist.write(visited_dir_path + "\n")

def can_update_visits_in_history_file(hist_file, update_dict, visited_path):
    entry_contained_in_file = False
    with open(hist_file, "r") as hist:
        for entry in hist.readlines():
            split_entry = entry.strip('\n').split(';')
            path = split_entry[0]
            if path == visited_path:
                update_dict[split_entry[0]] = int(split_entry[1]) + 1
                entry_contained_in_file = True
            else:
                update_dict[split_entry[0]] = int(split_entry[1])
    return entry_contained_in_file

update()
