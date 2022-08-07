import os
import display as out, navigation as nav, commands as cmd, common, clipboard as clip, recursive_transfer as rt, rename as rn

renaming_commands = {"ra", "ran", "rp", "rpn", "ri", "rin", "rd", "rr", "rrn"}
renaming_translations = {"ra" : "a", "ran" : "A", "rp" : "p", "rpn" : "P", "ri" : "i", "rin" : "I", "rd" : "d", "rr" : "r", "rrn" : "R"}
contextsDict = {":<" : "--execute", "::" : "--edit", "<" : "-h", "<<" : "-fh", ">" : "-f", "main" : ""}
validContexts = {"--execute", "--edit", "-h", "-fh", "-f", ""}

currentContext = "" # main context
currentFilter = "" # should change each time the user filters the navigation/command history

def execute():
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
    while True:
        if userInput not in {"?", "?clip", "?ren"}:
            out.displayGeneralOutput(prevDir) if len(prevCommand) == 0 else out.displayGeneralOutput(prevDir, prevCommand, commandResult)
        userInput = input()
        userInput = userInput.rstrip(' ') #there should be no trailing spaces, otherwise the entries might get duplicated in the navigation/command history
        while True:
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
    global currentContext
    global currentFilter
    handleOutput = 0
    shouldForwardData = False
    passedInput = ""
    passedOutput = ""
    shouldSwitchToMainContext = True #currently the app switches to main context each time input is entered in one of the main menus (to be updated)
    if userInput == "?":
        out.displayHelp()
    elif userInput == "?clip":
        out.displayClipboardHelp()
    elif userInput == "?ren":
        out.displayRenamingHelp()
    elif userInput == ":-":
        if len(prevCommand) == 0:
            print("No shell command previously executed")
        else:
            result = cmd.executeCommandWithStatus(prevCommand, True)
            shouldForwardData = True
    elif userInput == ":":
        result = cmd.editAndExecPrevCmd(prevCommand) if prevCommand != "" else cmd.editAndExecPrevCmd()
        handleOutput = 2 if result[0] == 0 else handleOutput
        shouldForwardData = True
    elif userInput == ":clearcommands":
        cmd.clearCommandHistory()
    elif len(userInput) >= 2 and (userInput[0:2] == ":<" or userInput[0:2] == "::"):
        outcome = setContext(contextsDict[userInput[0:2]], userInput[2:], handleOutput, shouldForwardData, prevCommand, prevDir, recursiveTransfer)
        result = outcome[0]
        handleOutput = outcome[1] if result is not None else handleOutput
        shouldForwardData = outcome[2] if result is not None else shouldForwardData
    elif len(userInput) >= 2 and userInput[0:2] == "<<":
        outcome = setContext(contextsDict[userInput[0:2]], userInput[2:], handleOutput, shouldForwardData, prevCommand, prevDir, recursiveTransfer)
        result = outcome[0]
        handleOutput = outcome[1] if result is not None else handleOutput
        shouldForwardData = outcome[2] if result is not None else shouldForwardData
    elif len(userInput) >= 1 and userInput[0] in ["<", ">"]:
        outcome = setContext(contextsDict[userInput[0]], userInput[1:], handleOutput, shouldForwardData, prevCommand, prevDir, recursiveTransfer)
        result = outcome[0]
        handleOutput = outcome[1] if result is not None else handleOutput
        shouldForwardData = outcome[2] if result is not None else shouldForwardData
    elif userInput == ",":
        result = nav.goTo(prevDir, os.getcwd())
        handleOutput = 4 if result[0] == 0 else handleOutput
        shouldForwardData = True
    elif userInput == "+>":
        nav.addDirToFavorites()
    elif userInput == "->":
        result = nav.removeDirFromFavorites()
        handleOutput = 1 if result[0] == 1 else handleOutput
        shouldForwardData = True
    elif userInput == ":clearnavigation":
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
    elif userInput.startswith(":") and userInput[1:] in renaming_commands:
        rn.rename(renaming_translations[userInput[1:]])
    elif len(userInput) > 1 and userInput[len(userInput)-1] == ":":
        print("Input cancelled, no action performed!")
    elif userInput == "!":
        print("You exited the navigation app.")
        print("")
        print("Last visited directory: " + os.getcwd())
        print("Last executed shell command: ", end='')
        print(prevCommand) if len(prevCommand) > 0 else print("none")
        print("")
    else:
        if userInput != "" and userInput[0] == ":":
            result = cmd.executeCommandWithStatus(userInput[1:])
            handleOutput = 2
        else:
            result = nav.goTo(userInput, prevDir)
            handleOutput = 4 if result[0] == 0 else handleOutput
        shouldForwardData = True
    if shouldForwardData:
        passedInput = result[1]
        passedOutput = result[2]
    if shouldSwitchToMainContext:
        setContext(contextsDict["main"], "", handleOutput, shouldForwardData, prevCommand, prevDir, recursiveTransfer)
    return (handleOutput, passedInput, passedOutput)

# contexts are related to main menus:
# - navigation history
# - filtered navigation history
# - favorites
# - command history in execute mode (filtered or not)
# - command history in edit mode (filtered or not)
# - main navigation mode (no main menu): includes all sub-contexts: edit an individual command, help menu, move/copy, recursive move/copy, renaming files/dirs etc
def setContext(newContext, userInput, outputHandling, shouldForwardInputOutput, previousCommand, previousDirectory, recursiveTransfer):
    global currentContext
    global currentFilter
    assert newContext in validContexts, "Invalid context detected"
    currentContext = newContext
    currentFilter = ""
    handleOutput = outputHandling
    shouldForwardData = shouldForwardInputOutput
    result = None
    if currentContext in ["--execute", "--edit"]:
        currentFilter = userInput
        result = cmd.visitCommandMenu(currentContext, currentFilter, previousCommand)
        handleOutput = 2 if result[0] == 0 else 1 if result[0] == 1 else handleOutput
        shouldForwardData = True
    elif currentContext in ["-f", "-h"]:
        result = nav.executeGoToFromMenu(currentContext, previousDirectory, userInput, previousCommand)
        if (len(userInput) > 0):
            handleOutput = 4 if result[0] == 0 else 1 if (result[0] == 1 or result[0] == 4) else handleOutput #forward user input if history menu is empty and the user enters <[entry_nr] (result == 4)
        else:
            handleOutput = 4 if result[0] <= 0 else 1 if result[0] == 1 else handleOutput
            if result[0] == -1:
                recursiveTransfer.setTargetDir(result[1])
        shouldForwardData = True
    elif currentContext == "-fh":
        if (len(userInput) > 0):
            currentFilter = userInput
            result = nav.executeGoToFromMenu(currentContext, previousDirectory, userInput, previousCommand)
            handleOutput = 4 if result[0] <= 0 else 1 if result[0] == 1 else handleOutput
            shouldForwardData = True
            if result[0] == -1:
                recursiveTransfer.setTargetDir(result[1])
        else:
            print("No filter keyword entered. Cannot filter navigation history.")

    return (result, handleOutput, shouldForwardData)

execute()
