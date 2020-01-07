import os, readline
import commands_backend as cmd

""" core command execution functions """
def executeCommand(command = "", repeatPrev = False):
    if command == "":
        print("No argument provided")
        result = (3, "", "")
    else:
        commandType = "Repeated" if repeatPrev == True else "Entered"
        print(commandType + " command is being executed: " + command)
        print("-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-")
        result = cmd.executeCommand(command) # have this updated, a return will be available
        print("-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-")
        print(commandType + " command finished " + result[2] + "! Scroll up to check output (if any) if it exceeds the screen.")
    return result

def editAndExecPrevCmd(previousCommand = ""):
    def hook():
        readline.insert_text(previousCommand)
        readline.redisplay()

    status = 0 #normal execution, no user abort
    passedInput = ""
    passedOutput = ""

    if previousCommand == "":
        print("No shell command executed in this session. Enter a new command")
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
        commandType = "Edited" if previousCommand != "" else "Entered"
        print(commandType + " command is being executed: " + commandToExecute)
        print("-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-")
        result = cmd.executeCommand(commandToExecute)
        print("-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-")
        print(commandType + " command finished " + result[2] + "! Scroll up to check output (if any) if it exceeds the screen.")
        passedInput = result[1]
        passedOutput = result[2]
    return (status, passedInput, passedOutput)

""" command menus functions """
def initCmdMenus():
    cmd.initCmdMenus()

def visitCommandMenu(mode = ""):
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
            if status == 2:
                print("You exited the command menu!")
        elif commandHistoryEntry != ":3" and commandHistoryEntry != ":4":
            if mode == "--execute":
                commandToExecute = commandHistoryEntry
                print("Repeated command is being executed: " + commandToExecute)
                print("-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-")
                result = cmd.executeCommand(commandToExecute)
                print("-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-")
                print("Repeated command finished " + result[2] + "! Scroll up to check output (if any) if it exceeds the screen.")
            else:
                result = editAndExecPrevCmd(commandHistoryEntry)
                if result[0] != 0:
                    status = 2 #aborted by user
            passedInput = result[1]
            passedOutput = result[2]
    return (status, passedInput, passedOutput)

def clearCommandHistory():
    cmd.clearCommandHistory()
    print("Content of command history menu has been erased.")
