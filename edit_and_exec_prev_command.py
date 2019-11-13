import sys, os, readline
import execute_command as cmd
from os.path import expanduser

home_dir = expanduser("~") + "/"

def edit_and_exec(previousCommand = ""):
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
        cmd.execute(commandToExecute)
        status = 0
    return status
