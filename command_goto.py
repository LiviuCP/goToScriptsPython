import sys, os, readline
import cmd_menus_update as cmd
from os.path import expanduser

home_dir = expanduser("~") + "/"

# 1) Go to command menu

def visitCommandMenu(mode = ""):
    # *** helper functions ***
    def displayCmdHistMenu(mode):
        print("COMMANDS LIST")
        print("")
        if mode == "--execute":
            print("-- EXECUTE MODE --")
        else:
            print("-- EDIT MODE--")
        print("")
        cmd.displayFormattedCmdHistContent()
        print("")
        print("Current directory: " + os.getcwd())
        print("")
        print("Enter command number.")
        print("Enter ! to quit.")
        print("")
    # *** actual function ***
    status = 0 # default status (normal execution)
    passedInput = ""
    passedOutput = ""
    if mode != "--edit" and mode != "--execute":
        print("Invalid argument provided")
        status = 3
    else:
        os.system("clear")
        if cmd.isCommandMenuEmpty():
            print("There are no entries in the command history menu.")
            userInput = ""
        else:
            displayCmdHistMenu(mode)
            userInput = input() # to update: enable path autocomplete
            os.system("clear")
        choiceResult = cmd.chooseCommand(userInput)
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
        result = cmd.executeCommand(commandToExecute)
        passedInput = result[1]
        passedOutput = result[2]
    return (status, passedInput, passedOutput)

# 3) Command menus initialization (wrapper for initCmdMenus)
def initCmdMenus():
    cmd.initCmdMenus()

# 4) Execute new command
def executeNewCommand(command = ""):
    if command == "":
        print("No argument provided")
        result = (3, "", "")
    else:
        result = cmd.executeCommand(command) # have this updated, a return will be available
    return result

# 5) Clear command history (wrapper for the cmd_menus_update function)
def clearCommandHistory():
    cmd.clearCommandHistory()
