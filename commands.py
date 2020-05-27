import os, readline
import commands_backend as cmd
from os.path import expanduser

home_dir = expanduser("~") + "/"
output_storage_file = home_dir + ".store_output" #used for communication with BASH
min_nr_of_cmd_chars = 10

""" core command execution function """
def executeCommand(command):
    assert len(command) > 0, "Empty command has been provided"
    # build and execute BASH command
    sourceConfigFileCmd = "source ~/.bashrc;" #include .bashrc to ensure the aliases and scripts work
    getExitCodeCmd = "echo $? > " + output_storage_file #exit code (used by Python to determine if the command finished successfully or not)
    bashCommandToExecute = sourceConfigFileCmd + "\n" + command + "\n" + getExitCodeCmd
    os.system(bashCommandToExecute)
    printedStatus = "with errors"
    # read command status code, create the status message and update the command history files
    with open(output_storage_file, "r") as output:
        if int(output.readline().strip('\n')) == 0:
            printedStatus = "successfully"
        if len(command) >= min_nr_of_cmd_chars:
            cmd.updateCommandHistory(command)
            cmd.consolidateCommandHistory()
    return (0, command, printedStatus)

""" core command execution function wrappers """
def executeCommandWithStatus(command = "", repeatPrev = False):
    assert len(command) > 0, "Empty argument detected for 'command'"
    commandType = "Repeated" if repeatPrev == True else "Entered"
    print(commandType + " command is being executed: " + command)
    print("-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-")
    result = executeCommand(command)
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
    commandToExecute = commandToExecute.rstrip(' ') #there should be no trailing spaces, otherwise the entries might get duplicated in the command history
    readline.set_pre_input_hook() # ensure any further input is no longer pre-filled
    os.system("clear")
    if commandToExecute == "" or commandToExecute[len(commandToExecute)-1] == ':':
        print("Command aborted. You returned to navigation menu.")
        status = 1
    else:
        commandType = "Edited" if previousCommand != "" else "Entered"
        print(commandType + " command is being executed: " + commandToExecute)
        print("-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-")
        result = executeCommand(commandToExecute)
        print("-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-")
        print(commandType + " command finished " + result[2] + "! Scroll up to check output (if any) if it exceeds the screen.")
        passedInput = result[1]
        passedOutput = result[2]
    return (status, passedInput, passedOutput)

""" command menus functions """
def initCmdMenus():
    cmd.initCmdMenus()

def visitCommandMenu(mode, filterKey = ""):
    def displayCommandMenuFooter():
        print("")
        print("Current directory: " + os.getcwd())
        print("")
        print("Enter command number.")
        print("Enter ! to quit.")
        print("")
    def displayCmdHistMenu(mode):
        print("COMMANDS LIST")
        print("")
        print("**** EXECUTE MODE ****") if mode == "--execute" else print("**** EDIT MODE ****")
        print("")
        print("-- RECENTLY EXECUTED --")
        print("")
        cmd.displayFormattedRecentCmdHistContent()
        print("")
        print("-- MOST EXECUTED --")
        print("")
        cmd.displayFormattedPersistentCmdHistContent()
        displayCommandMenuFooter()
    def displayFilteredCmdHistMenu(content, mode, totalNrOfMatches):
        print("FILTERED COMMANDS LIST")
        print("")
        print("**** EXECUTE MODE ****") if mode == "--execute" else print("**** EDIT MODE ****")
        print("")
        cmd.displayFormattedFilteredCmdHistContent(content, totalNrOfMatches)
        displayCommandMenuFooter()
    status = 0 # default status (normal execution)
    passedInput = ""
    passedOutput = ""
    assert mode in ["--edit", "--execute"], "Invalid mode argument provided"
    os.system("clear")
    filteredHistEntries = []
    if cmd.isCommandMenuEmpty():
        print("There are no entries in the command history menu.")
        userInput = ""
    elif len(filterKey) == 0:
        displayCmdHistMenu(mode)
        userInput = input()
        os.system("clear")
    else:
        totalNrOfMatches = cmd.buildFilteredCommandHistory(filteredHistEntries, filterKey)
        if len(filteredHistEntries) == 0:
            print("There are no entries in the filtered command history menu.")
            userInput = ""
        else:
            displayFilteredCmdHistMenu(filteredHistEntries, mode, totalNrOfMatches)
            userInput = input()
            os.system("clear")
    # process user choice
    choiceResult = cmd.chooseCommand(userInput) if len(filterKey) == 0 else cmd.chooseFilteredCommand(userInput, filteredHistEntries)
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
            result = executeCommand(commandToExecute)
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
