import sys, os
import cmd_menus_update as cmd
import edit_and_exec_prev_command as editprev
from os.path import expanduser

home_dir = expanduser("~") + "/"
input_storage_file = home_dir + ".store_input"
output_storage_file = home_dir + ".store_output"

# solve the multiple return points !!!
def visit_command_menu(commandMode = ""):
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
            status = editprev.edit_and_exec(commandHistoryEntry)
            if status == 0:
                return 0 #command got executed
            else:
                return 2 #aborted by user
