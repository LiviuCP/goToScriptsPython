import sys, os
from os.path import expanduser

home_dir = expanduser("~") + "/"
c_hist_file = home_dir + ".command_history"
input_storage_file = home_dir + ".store_input"
output_storage_file = home_dir + ".store_output"

# The result returned by this method is stored into the .store_output file to be picked by the BASH script
# It can have following values: a BASH command or a specific code that indicates a certain behavior:
# :1 - user input stored in .store_input, to be picked and forwarded by BASH
# :2 - user exited the choose path dialog, no further actions
# :3 - invalid or missing first argument sys.argv[1]
# :4 - empty history or favorites file
def chooseCommand():
    command = ""
    outcome = "none" #check if really needed
    editCommand = False

    if len(sys.argv) == 1:
        print("no option provided")
        outcome = ":3"
    elif sys.argv[1] != "--edit" and sys.argv[1] != "--execute":
        print("invalid option provided")
        outcome = ":3"
    else:
        outcome = chooseCommandFromHistoryMenu(sys.argv[1])

    with open(output_storage_file, "w") as output_storage:
        output_storage.write(outcome)

def chooseCommandFromHistoryMenu(mode):
    with open(c_hist_file, "r") as c_hist:
        c_hist_content = c_hist.readlines()
    os.system("clear")
    c_hist_entries = len(c_hist_content)
    line_nr = 1
    if c_hist_entries == 0:
        print("There are no entries in the command history menu.")
        user_input = ""
    else:
        if mode == "--execute":
            print("-- EXECUTE COMMAND --")
        else:
            print("-- EDIT COMMAND --")
        print("")
        while line_nr <= c_hist_entries:
            entry = c_hist_content[line_nr-1].strip('\n')
            print('{0:<10s} {1:<140s}'.format(str(line_nr), entry))
            line_nr = line_nr + 1
        print("")
        print("Current directory: " + os.getcwd())
        print("")
        print("Enter command number.")
        print("Enter ! to quit.")
        print("")

        # to update: enable path autocomplete
        user_input = input()
        os.system("clear")

    return getOutput(user_input, c_hist_content)

# duplicate to the function from choose_path_from_menu.py, handle later
def getOutput(user_input, content):
    if len(content) == 0:
        output = ":4"
    elif isValidInput(user_input, content):
        user_input = int(user_input) - 1
        output = content[user_input]
    elif user_input == '!':
        print("No command chosen!")
        output = ":2"
    else:
        # input to be forwarded for further handling to BASH
        with open(input_storage_file, "w") as input_storage:
            input_storage.write(user_input)
        output = ":1"
    return output

# duplicate to the function from choose_path_from_menu.py, handle later
def isValidInput(user_input, content):
    is_valid = True
    if user_input.isdigit():
        int_input = int(user_input)
        if int_input > len(content) or int_input == 0:
            is_valid = False
    else:
        is_valid = False
    return is_valid

chooseCommand()
