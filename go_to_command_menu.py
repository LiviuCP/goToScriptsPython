import sys, os
import choose_command_from_menu as menucommand
import execute_command as cmd
import edit_and_exec_prev_command as editprev
from os.path import expanduser

home_dir = expanduser("~") + "/"
input_storage_file = home_dir + ".store_input"
output_storage_file = home_dir + ".store_output"

def visit_command_menu():
    if len(sys.argv) < 2:
        print("Insufficient number of arguments")
        sys.exit(3)
    else:
        mode = sys.argv[1]
        commandHistoryEntry = menucommand.chooseCommand(mode)

    if commandHistoryEntry == ":1":
        sys.exit(1) #forward user input
    elif commandHistoryEntry == ":2": #aborted by user
        sys.exit(2)
    elif commandHistoryEntry != ":3" and commandHistoryEntry != ":4":
        if mode == "--execute":
            commandToExecute = commandHistoryEntry
            prevCommand = commandToExecute
            cmd.execute(commandToExecute)
            sys.exit(0)
        else:
            status = editprev.edit_and_exec(commandHistoryEntry)
            if status == 0:
                sys.exit(0) #command got executed
            else:
                sys.exit(2) #aborted by user

visit_command_menu()
