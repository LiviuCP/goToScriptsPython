import sys, os, readline
import cmd_menus_update as cmd
from os.path import expanduser

home_dir = expanduser("~") + "/"

# 1) Go to command menu

def visitCommandMenu(commandMode = ""):
    status = 0 # default status (normal execution)
    passedInput = ""
    passedOutput = ""
    if commandMode == "":
        print("Insufficient number of arguments")
        status = 3
    else:
        mode = commandMode
        choiceResult = cmd.chooseCommand(mode)
        commandHistoryEntry = choiceResult[0]
        if commandHistoryEntry == ":1" or commandHistoryEntry == ":2":
            status = int(commandHistoryEntry[1])
            passedInput = choiceResult[1]
        elif commandHistoryEntry != ":3" and commandHistoryEntry != ":4":
            if mode == "--execute":
                commandToExecute = commandHistoryEntry
                result = cmd.executeCommand(commandToExecute)
            else:
                result = editAndExecPrevCmd(commandHistoryEntry)
                if result[0] != 0:
                    status = 2 #aborted by user
            passedInput = result[1]
            passedOutput = result[2]
    return (status, passedInput, passedOutput)

# 2) Edit and execute previous command
def editAndExecPrevCmd(previousCommand = ""):
    def hook():
        readline.insert_text(previousCommand)
        readline.redisplay()

    status = 0 #normal execution, no user abort
    passedInput = ""
    passedOutput = ""

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
        result = cmd.executeCommand(commandToExecute) # have this updated (return available)
        passedInput = result[1]
        passedOutput = result[2]
    return (status, passedInput, passedOutput)
