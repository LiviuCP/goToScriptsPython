import os
import display as out, navigation as nav, commands as cmd, common, clipboard as clip, recursive_transfer as rt

syncWithFinder = False
closeFinder = True # set this variable to False if Finder should stay open when sync is toggled to off via :s command

def execute():
    global syncWithFinder
    common.setPathAutoComplete()
    nav.initNavMenus()
    cmd.initCmdMenus()
    prevDir = os.getcwd()
    prevCommand = ""
    commandResult = ""
    userInput = ""
    forwardUserInput = False
    clipboard = clip.Clipboard()
    recursiveTransfer = rt.RecursiveTransfer()
    os.system("clear")
    print("Welcome to navigation app!")
    while True == True:
        if userInput != "?":
            out.displayGeneralOutput(prevDir, syncWithFinder) if prevCommand == "" else out.displayGeneralOutput(prevDir, syncWithFinder, prevCommand, commandResult)
        userInput = input()
        while True == True:
            os.system("clear")
            result = handleUserInput(userInput, prevDir, prevCommand, clipboard, recursiveTransfer)
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
def handleUserInput(userInput, prevDir, prevCommand, clipboard, recursiveTransfer):
    global syncWithFinder
    handleOutput = 0
    passedInput = ""
    passedOutput = ""
    shouldForwardData = False
    if userInput == "?":
        out.displayHelp()
    elif userInput == ":-":
        if prevCommand == "":
            print("No shell command previously executed")
        else:
            result = cmd.executeCommandWithStatus(prevCommand, True)
            shouldForwardData = True
    elif userInput == ":":
        result = cmd.editAndExecPrevCmd(prevCommand) if prevCommand != "" else cmd.editAndExecPrevCmd()
        handleOutput = 2 if result[0] == 0 else handleOutput
        shouldForwardData = True
    elif userInput == "::<>":
        cmd.clearCommandHistory()
    elif userInput == ":<":
        result = cmd.visitCommandMenu("--execute")
        handleOutput = 2 if result[0] == 0 else 1 if result[0] == 1 else handleOutput
        shouldForwardData = True
    elif len(userInput) > 2 and userInput[0:2] == ":<":
        result = cmd.visitCommandMenu("--execute", userInput[2:])
        handleOutput = 2 if result[0] == 0 else 1 if result[0] == 1 else handleOutput
        shouldForwardData = True
    elif userInput == "::":
        result = cmd.visitCommandMenu("--edit")
        handleOutput = 2 if result[0] == 0 else 1 if result[0] == 1 else handleOutput
        shouldForwardData = True
    elif len(userInput) > 2 and userInput[0:2] == "::":
        result = cmd.visitCommandMenu("--edit", userInput[2:])
        handleOutput = 2 if result[0] == 0 else 1 if result[0] == 1 else handleOutput
        shouldForwardData = True
    elif userInput == "<":
        result = nav.executeGoToFromMenu("-h", prevDir, syncWithFinder)
        handleOutput = 4 if result[0] <= 0 else 1 if result[0] == 1 else handleOutput
        shouldForwardData = True
        if result[0] == -1:
            recursiveTransfer.setTargetDir(result[1])
    elif userInput == ">":
        result = nav.executeGoToFromMenu("-f", prevDir, syncWithFinder)
        handleOutput = 4 if result[0] <= 0 else 1 if result[0] == 1 else handleOutput
        shouldForwardData = True
        if result[0] == -1:
            recursiveTransfer.setTargetDir(result[1])
    elif len(userInput) > 1 and userInput[0] == "<":
        result = nav.executeGoToFromMenu("-h", prevDir, syncWithFinder, userInput[1:])
        handleOutput = 4 if result[0] == 0 else 1 if (result[0] == 1 or result[0] == 4) else handleOutput #forward user input if history menu is empty and the user enters <[entry_nr] (result == 4)
        shouldForwardData = True
    elif len(userInput) > 1 and userInput[0] == ">":
        result = nav.executeGoToFromMenu("-f", prevDir, syncWithFinder, userInput[1:])
        handleOutput = 4 if result[0] == 0 else 1 if (result[0] == 1 or result[0] == 4) else handleOutput #forward user input if favorites menu is empty and the user enters >[entry_nr] (result == 4)
        shouldForwardData = True
    elif userInput == ",":
        result = nav.goTo(prevDir, os.getcwd(), syncWithFinder)
        handleOutput = 4 if result[0] == 0 else handleOutput
        shouldForwardData = True
    elif userInput == "+>":
        nav.addDirToFavorites()
    elif userInput == "->":
        result = nav.removeDirFromFavorites()
        handleOutput = 1 if result[0] == 1 else handleOutput
        shouldForwardData = True
    elif userInput == ":<>":
        nav.clearVisitedDirsMenu()
    elif userInput == ":c":
        clipboard.createAction()
    elif userInput == ":m":
        clipboard.createAction(False)
    elif userInput == ":y":
        clipboard.applyAction()
    elif userInput == ":ec":
        clipboard.erase(True)
    elif userInput == ":dc":
        clipboard.display()
    elif userInput == ":td":
        recursiveTransfer.setTargetDir()
    elif userInput == ":M":
        recursiveTransfer.transferItemsToTargetDir(False)
    elif userInput == ":C":
        recursiveTransfer.transferItemsToTargetDir()
    elif userInput == ":etd":
        recursiveTransfer.eraseTargetDir(True)
    elif userInput == ":dtd":
        recursiveTransfer.displayTargetDir()
    elif len(userInput) > 1 and userInput[len(userInput)-1] == ":":
        print("Input cancelled, no action performed!")
    elif userInput == ":s":
        print("Finder synchronization enabled") if syncWithFinder == False else print("Finder synchronization disabled")
        syncWithFinder = not syncWithFinder
        if syncWithFinder == True:
            nav.doFinderSync()
        elif closeFinder == True:
            nav.doCloseFinder()
    elif userInput == "!":
        print("You exited navigation app.")
        print("Last visited directory: " + os.getcwd())
    else:
        if userInput != "" and userInput[0] == ":":
            result = cmd.executeCommandWithStatus(userInput[1:])
            handleOutput = 2
        else:
            result = nav.goTo(userInput, prevDir, syncWithFinder)
            handleOutput = 4 if result[0] == 0 else handleOutput
        shouldForwardData = True
    if shouldForwardData == True:
        passedInput = result[1]
        passedOutput = result[2]
    return (handleOutput, passedInput, passedOutput)

execute()
