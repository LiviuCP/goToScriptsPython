import os
import display as out, navigation as nav, commands as cmd, common, clipboard

def execute():
    common.setPathAutoComplete()
    nav.initNavMenus()
    cmd.initCmdMenus()
    prevDir = os.getcwd()
    prevCommand = ""
    commandResult = ""
    userInput = ""
    forwardUserInput = False
    os.system("clear")
    print("Welcome to navigation app!")
    while True == True:
        if userInput != "?":
            out.displayGeneralOutput(prevDir) if prevCommand == "" else out.displayGeneralOutput(prevDir, prevCommand, commandResult)
        userInput = input()
        while True == True:
            os.system("clear")
            result = handleUserInput(userInput, prevDir, prevCommand)
            if result[0] == 1:
                userInput = result[1]
                forwardUserInput = True
            elif result[0] == 2:
                prevCommand = result[1]
                commandResult = result[2]
            elif result[0] == 4:
                prevDir = result[2]
            if forwardUserInput == True:
                forwardUserInput = False
            else:
                break
        if userInput == "!":
            break

""" return codes: -1 - goTo not successfully executed, 0 - no action performed (returned by default unless otherwise mentioned), 1 - forward input to BASH, 2 - update prevCommand and commandResult, 3 - no arguments, 4 - update prev dir and cd """
def handleUserInput(userInput, prevDir, prevCommand):
    handleOutput = 0
    passedInput = ""
    passedOutput = ""
    shouldForwardData = True
    if userInput == "?":
        out.displayHelp()
        shouldForwardData = False
    elif userInput == ":-":
        if prevCommand == "":
            print("No shell command previously executed")
            shouldForwardData = False
        else:
            result = cmd.executeCommand(prevCommand, True)
    elif userInput == ":":
        result = cmd.editAndExecPrevCmd(prevCommand) if prevCommand != "" else cmd.editAndExecPrevCmd()
        handleOutput = 2 if result[0] == 0 else handleOutput
    elif userInput == ":<":
        result = cmd.visitCommandMenu("--execute")
        handleOutput = 2 if result[0] == 0 else 1 if result[0] == 1 else handleOutput
    elif userInput == "::":
        result = cmd.visitCommandMenu("--edit")
        handleOutput = 2 if result[0] == 0 else 1 if result[0] == 1 else handleOutput
    elif userInput == "::<>":
        cmd.clearCommandHistory()
        shouldForwardData = False
    elif userInput == "<":
        result = nav.executeGoToFromMenu("-h", prevDir)
        handleOutput = 4 if result[0] == 0 else 1 if result[0] == 1 else handleOutput
    elif userInput == ">":
        result = nav.executeGoToFromMenu("-f", prevDir)
        handleOutput = 4 if result[0] == 0 else 1 if result[0] == 1 else handleOutput
    elif len(userInput) > 1 and userInput[0] == "<":
        result = nav.executeGoToFromMenu("-h", prevDir, userInput[1:])
        handleOutput = 4 if result[0] == 0 else 1 if (result[0] == 1 or result[0] == 4) else handleOutput #forward user input if history menu is empty and the user enters <[entry_nr] (result == 4)
    elif len(userInput) > 1 and userInput[0] == ">":
        result = nav.executeGoToFromMenu("-f", prevDir, userInput[1:])
        handleOutput = 4 if result[0] == 0 else 1 if (result[0] == 1 or result[0] == 4) else handleOutput #forward user input if favorites menu is empty and the user enters >[entry_nr] (result == 4)
    elif userInput == ",":
        result = nav.goTo(prevDir, os.getcwd())
        handleOutput = 4 if result[0] == 0 else handleOutput
    elif userInput == "+>":
        nav.addDirToFavorites()
        shouldForwardData = False
    elif userInput == "->":
        result = nav.removeDirFromFavorites()
        handleOutput = 1 if result[0] == 1 else handleOutput
    elif userInput == ":<>":
        nav.clearVisitedDirsMenu()
        shouldForwardData = False
    elif userInput == ":c":
        clipboard.createAction()
        shouldForwardData = False
    elif userInput == ":m":
        clipboard.createAction(False)
        shouldForwardData = False
    elif userInput == ":y":
        clipboard.applyAction()
        shouldForwardData = False
    elif userInput == ":ec":
        clipboard.erase()
        shouldForwardData = False
    elif userInput == ":dc":
        clipboard.display()
        shouldForwardData = False
    elif userInput == ":td":
        clipboard.setTargetDir()
        shouldForwardData = False
    elif len(userInput) > 1 and userInput[len(userInput)-1] == ":":
        shouldForwardData = False
        print("Input cancelled, no action performed!")
    elif userInput == "!":
        shouldForwardData = False
        print("You exited navigation app.")
        print("Last visited directory: " + os.getcwd())
    else:
        if userInput != "" and userInput[0] == ":":
            result = cmd.executeCommand(userInput[1:])
            handleOutput = 2
        else:
            result = nav.goTo(userInput, prevDir)
            handleOutput = 4 if result[0] == 0 else handleOutput
    if shouldForwardData == True:
        passedInput = result[1]
        passedOutput = result[2]
    return (handleOutput, passedInput, passedOutput)

execute()
