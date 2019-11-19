import sys, os, readline
import cmd_menus_update as cmd
from os.path import expanduser

home_dir = expanduser("~") + "/"
input_storage_file = home_dir + ".store_input"
output_storage_file = home_dir + ".store_output"

# 1) Go to command menu

# solve the multiple return points !!!
def visitCommandMenu(commandMode = ""):
    if commandMode == "":
        print("Insufficient number of arguments")
        return 3
    else:
        mode = commandMode
        commandHistoryEntry = cmd.chooseCommand(mode)

    if commandHistoryEntry == ":1":
        return 1 #forward user input
    elif commandHistoryEntry == ":2": #aborted by user
        return 2
    elif commandHistoryEntry != ":3" and commandHistoryEntry != ":4":
        if mode == "--execute":
            commandToExecute = commandHistoryEntry
            prevCommand = commandToExecute
            cmd.executeCommand(commandToExecute)
            return 0
        else:
            status = editAndExecPrevCmd(commandHistoryEntry)
            if status == 0:
                return 0 #command got executed
            else:
                return 2 #aborted by user

# 2) Edit and execute previous command
def editAndExecPrevCmd(previousCommand = ""):
    def hook():
        readline.insert_text(previousCommand)
        readline.redisplay()

    if previousCommand == "":
        print("No shell command previously executed. Enter a new command")
    else:
        print("Please edit the below command and hit ENTER to execute")
        readline.set_pre_input_hook(hook)

    print("(press \':\' + ENTER to quit):")
    commandToExecute = input()
    readline.set_pre_input_hook() # ensure any further input is no longer pre-filled

    os.system("clear")
    if commandToExecute == "" or commandToExecute[len(commandToExecute)-1] == ':':
        print("Command aborted. You returned to navigation menu.")
        status = 1
    else:
        cmd.executeCommand(commandToExecute)
        status = 0
    return status
