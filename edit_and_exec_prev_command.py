import sys, os, readline
import execute_command as cmd
from os.path import expanduser

home_dir = expanduser("~") + "/"
input_storage_file = home_dir + ".store_input"

def edit_and_exec():
    if len(sys.argv) == 1 or sys.argv[1] == "":
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
        sys.exit(1)
    else:
        # forward input command to BASH for further usage
        with open(input_storage_file, "w") as input_storage:
            input_storage.write(commandToExecute)
        cmd.execute(commandToExecute)
        sys.exit(0)

def hook():
    prevCommand = sys.argv[1]
    readline.insert_text(prevCommand)
    readline.redisplay()

edit_and_exec()
