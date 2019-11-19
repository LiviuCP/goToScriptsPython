# common code to be used by cmd_menus.update.py and nav_menus_update.py

def limitEntriesNr(file_path, max_entries):
    with open(file_path, "r") as f:
        file_content = f.readlines()
        file_entries = 0
        for entry in file_content:
            file_entries = file_entries + 1
    if file_entries > max_entries:
        with open(file_path, "w") as f:
            for entry_nr in range(0, max_entries):
                f.write(file_content[entry_nr])
