from os.path import expanduser

home_dir = expanduser("~") + "/"
input_storage_file = home_dir + ".store_input"

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

def getOutput(user_input, content, menu_type):
    def isInputValid(user_input, content):
        is_valid = True
        if user_input.isdigit():
            int_input = int(user_input)
            if int_input > len(content) or int_input == 0:
                is_valid = False
        else:
            is_valid = False
        return is_valid
    if len(content) == 0:
        # input (if any, like when user enters >1 or <2) to be forwarded for further handling to BASH
        with open(input_storage_file, "w") as input_storage:
            input_storage.write(user_input)
        output = ":4"
    elif isInputValid(user_input, content):
        user_input = int(user_input) - 1
        output = content[user_input]
    elif user_input == '!':
        print("You exited " + menu_type + " menu!")
        output = ":2"
    else:
        # input to be forwarded for further handling to BASH
        with open(input_storage_file, "w") as input_storage:
            input_storage.write(user_input)
        output = ":1"
    return output
