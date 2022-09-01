import os, readline
import commands_backend as cmd, common

""" core command execution function """
def executeCommand(command):
    assert len(command) > 0, "Empty command has been provided"
    # build and execute BASH command
    bashCommandToExecute = cmd.buildShellCommand(command)
    os.system(bashCommandToExecute)
    # read command status code, create the status message and update the command history files
    commandExecResult = cmd.retrieveCommandExecResult()
    finishingStatus = "successfully" if commandExecResult == 0 else "with errors"
    if len(command) >= cmd.getMinCommandSize():
        cmd.updateCommandHistory(command)
        cmd.consolidateCommandHistory()
    return (0, command, finishingStatus)

""" core command execution function wrappers """
def executeCommandWithStatus(command = "", repeatPrev = False):
    assert len(command) > 0, "Empty argument detected for 'command'"
    commandType = "Repeated" if repeatPrev == True else "Entered"
    print(commandType + " command is being executed: " + command)
    print("-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-")
    result = executeCommand(command)
    finishingStatus = result[2]
    print("-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-")
    print(commandType + " command finished " + finishingStatus + "! Scroll up to check output (if any) if it exceeds the screen.")
    return result

def editAndExecPrevCmd(previousCommand = ""):
    def hook():
        readline.insert_text(previousCommand)
        readline.redisplay()
    status = 0 #normal execution, no user abort
    passedInput = ""
    passedOutput = ""
    if len(previousCommand) == 0:
        print("No shell command executed in this session. Enter a new command")
    else:
        print("Please edit the below command and hit ENTER to execute")
        readline.set_pre_input_hook(hook)
    print("(press \':\' + ENTER to quit):")
    commandToExecute = input()
    commandToExecute = commandToExecute.rstrip(' ') #there should be no trailing spaces, otherwise the entries might get duplicated in the command history
    readline.set_pre_input_hook() # ensure any further input is no longer pre-filled
    os.system("clear")
    commandLength = len(commandToExecute)
    if commandLength > 0 and commandToExecute[commandLength-1] != ':':
        commandType = "Edited" if previousCommand != "" else "Entered"
        print(commandType + " command is being executed: " + commandToExecute)
        print("-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-")
        result = executeCommand(commandToExecute)
        finishingStatus = result[2]
        print("-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-")
        print(commandType + " command finished " + finishingStatus + "! Scroll up to check output (if any) if it exceeds the screen.")
        passedInput = result[1]
        passedOutput = finishingStatus
    else:
        print("Command aborted. You returned to navigation menu.")
        status = 2 #aborted by user
    return (status, passedInput, passedOutput)

""" command menus functions """
def initCmdMenus():
    cmd.initCmdMenus()

def visitCommandMenu(mode, filterKey = "", previousCommand = ""):
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
    def displayFilteredCmdHistMenu(content, mode, totalNrOfMatches):
        print("FILTERED COMMANDS LIST")
        print("")
        print("**** EXECUTE MODE ****") if mode == "--execute" else print("**** EDIT MODE ****")
        print("")
        cmd.displayFormattedFilteredCmdHistContent(content, totalNrOfMatches)
    def displayPageFooter(filterKey = ""):
        print("")
        print("Current directory: " + os.getcwd())
        print("Last executed shell command: ", end='')
        print(previousCommand) if len(previousCommand) > 0 else print("none")
        print("")
        if len(filterKey) > 0:
            print("Applied filter: " + filterKey)
            print("")
        print("Enter command number.")
        print("Enter :t to toggle to ", end='')
        print("EDIT MODE.") if mode == "--execute" else print("EXECUTE MODE.")
        print("")
        print("Enter ! to quit.")
        print("")
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
        displayPageFooter()
        userInput = input()
        os.system("clear")
    else:
        filterResult = cmd.buildFilteredCommandHistory(filteredHistEntries, filterKey)
        totalNrOfMatches = filterResult[0]
        appliedFilterKey = filterResult[1]
        if len(filteredHistEntries) == 0:
            print("There are no entries in the filtered command history menu.")
            userInput = ""
        else:
            displayFilteredCmdHistMenu(filteredHistEntries, mode, totalNrOfMatches)
            displayPageFooter(appliedFilterKey)
            userInput = input()
            os.system("clear")
    # process user choice
    choiceResult = cmd.chooseCommand(userInput) if len(filterKey) == 0 else cmd.chooseFilteredCommand(userInput, filteredHistEntries)
    commandHistoryEntry = choiceResult[0]
    if commandHistoryEntry in [":1", ":2"]:
        status = int(commandHistoryEntry[1])
        passedInput = choiceResult[1]
        if status == 2:
            print("You exited the command menu!")
    elif commandHistoryEntry not in [":3", ":4"]:
        if mode == "--execute":
            commandToExecute = commandHistoryEntry
            if cmd.isSensitiveCommand(commandToExecute):
                print("The following command might cause ireversible changes:")
                print(commandToExecute)
                print("")
                print("Current directory: ")
                print(os.getcwd())
                print("")
                print("Are you sure you want to continue?")
                print("")
                choice = common.getInputWithTextCondition("Enter your choice (y/n): ", lambda userInput: userInput.lower() not in {'y', 'n'}, \
                                                          "Invalid choice selected. Please try again")
                os.system("clear")
                if choice.lower() == "n":
                    commandToExecute = None
                    result = (2, "", "")
                    status = result[0]
                    print("Command aborted. You returned to navigation menu.")
            if commandToExecute is not None:
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
