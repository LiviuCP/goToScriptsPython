# 1) Choose command from menu
import sys, os, datetime
from os.path import expanduser

home_dir = expanduser("~") + "/"
c_hist_file = home_dir + ".command_history"
c_r_hist_file = home_dir + ".recent_command_history"
input_storage_file = home_dir + ".store_input"
output_storage_file = home_dir + ".store_output"
c_r_hist_max_entries = 25
minNrOfCmdChars = 10

# The result returned by this method is stored into the .store_output file to be picked by the BASH script
# It can have following values: a BASH command or a specific code that indicates a certain behavior:
# :1 - user input stored in .store_input, to be picked and forwarded by BASH
# :2 - user exited the choose path dialog, no further actions
# :3 - invalid or missing first argument sys.argv[1] (no more used)
# :4 - empty history or favorites file
def chooseCommand(mode = ""):
    editCommand = False
    if mode == "":
        print("no argument provided")
        outcome = ":3"
    elif mode != "--edit" and mode != "--execute":
        print("invalid argument provided")
        outcome = ":3"
    else:
        outcome = chooseCommandFromHistoryMenu(mode).strip('\n')
    return outcome

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

# 2) Execute new command
def executeNewCommand(command = ""):
    if command == "":
        print("No argument provided")
    else:
        executeCommand(command)

# 3) Execute command
def executeCommand(commandToExecute):
    if len(commandToExecute) >= minNrOfCmdChars:
        updateIndividualCommandHistoryFiles(commandToExecute)
        consolidateCommandHistory()

    print("Command is being executed: " + commandToExecute)
    print("--------------------------")

    # build and execute command
    sourceCommand = "source ~/.bashrc;" #include .bashrc to ensure the aliases and scripts work
    executionStatus = "echo $? > " + output_storage_file
    executeCommandWithStatus = sourceCommand + "\n" + commandToExecute + "\n" + executionStatus
    os.system(executeCommandWithStatus)

    # read command status code and create the status message
    with open(output_storage_file, "r") as output:
        status = output.readline().strip('\n')
        printedStatus = "with errors" if status != "0" else "successfully"

    # status message to be written instead of code so it's used by BASH to indicate how the last executed command finished (to be updated)
    with open(output_storage_file, "w") as output:
        output.write(printedStatus)
    # forward input command to BASH for further usage
    with open(input_storage_file, "w") as input_storage:
        input_storage.write(commandToExecute)

    print("--------------------------")
    print("Command finished " + printedStatus + "! Scroll up to check output (if any) if it exceeds the screen.")

def updateIndividualCommandHistoryFiles(command):
    with open(c_r_hist_file, "r") as c_r_hist:
        c_r_hist_content = []
        c_r_hist_entries = 0
        for entry in c_r_hist.readlines():
            c_r_hist_content.append(entry.strip('\n'))
            c_r_hist_entries = c_r_hist_entries + 1

    if command in c_r_hist_content:
        c_r_hist_content.remove(command)
    elif c_r_hist_entries == c_r_hist_max_entries:
        c_r_hist_content.remove(c_r_hist_content[c_r_hist_entries-1])
    c_r_hist_content = [command] + c_r_hist_content

    with open(c_r_hist_file, "w") as c_r_hist:
        for entry in c_r_hist_content:
            c_r_hist.write(entry+'\n')

# 4) Consolidate command history
def consolidateCommandHistory():
    with open(c_r_hist_file, 'r') as c_r_hist:
        c_r_hist_entries = c_r_hist.readlines()
        c_r_hist_entries.sort()

    with open(c_hist_file, 'w') as c_hist:             # always ensure the file is cleared before (re-)consolidating history
        for entry in c_r_hist_entries:
            c_hist.write(entry)

# 5) Clear command history
def clearCommandHistory():
    #erase all files related to command history
    with open(c_r_hist_file, "w") as c_r_hist:
        c_r_hist.write("")
    with open(c_hist_file, "w") as c_hist:
        c_hist.write("")

    print("Content of command history menu has been erased.")
