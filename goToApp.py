import os
import display as out, navigation as nav, commands as cmd

def execute():
    nav.initNavMenus()
    cmd.initCmdMenus()
    prevDir = os.getcwd()
    prevCommand = ""
    commandResult = ""
    navigationInput = ""
    forwardUserInput = False
    os.system("clear")
    print("Welcome to navigation mode!")
    while True == True:
        if navigationInput != "?":
            if prevCommand == "":
                out.displayGeneralNavOutput()
            else:
                out.displayGeneralNavOutput(prevCommand, commandResult)
        navigationInput = input()
        while True == True:
            os.system("clear")
            result = handleUserInput(navigationInput, prevDir, prevCommand)
            if result[0] == 1:
                navigationInput = result[1]
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
        if navigationInput == "!":
            break

""" return codes: -1 - goTo not successfully executed, 0 - no action performed (returned by default unless otherwise mentioned), 1 - forward input to BASH, 2 - update prevCommand and commandResult, 3 - no arguments, 4 - update prev dir and cd """
def handleUserInput(navigationInput, prevDir, prevCommand):
    navigationOutput = 0
    passedInput = ""
    passedOutput = ""
    shouldForwardData = True
    if navigationInput == "?":
        out.displayHelp()
        shouldForwardData = False
    elif navigationInput == ":-":
        if prevCommand == "":
            print("No shell command previously executed")
            shouldForwardData = False
        else:
            result = cmd.executeCommand(prevCommand, True)
    elif navigationInput == ":":
        result = cmd.editAndExecPrevCmd(prevCommand) if prevCommand != "" else cmd.editAndExecPrevCmd()
        navigationOutput = 2 if result[0] == 0 else navigationOutput
    elif navigationInput == ":<":
        result = cmd.visitCommandMenu("--execute")
        navigationOutput = 2 if result[0] == 0 else 1 if result[0] == 1 else navigationOutput
    elif navigationInput == "::":
        result = cmd.visitCommandMenu("--edit")
        navigationOutput = 2 if result[0] == 0 else 1 if result[0] == 1 else navigationOutput
    elif navigationInput == "::<>":
        cmd.clearCommandHistory()
        shouldForwardData = False
    elif navigationInput == "<":
        result = nav.visitNavigationMenu("-h", prevDir)
        navigationOutput = 4 if result[0] == 0 else 1 if result[0] == 1 else navigationOutput
    elif navigationInput == ">":
        result = nav.visitNavigationMenu("-f", prevDir)
        navigationOutput = 4 if result[0] == 0 else 1 if result[0] == 1 else navigationOutput
    elif len(navigationInput) > 1 and navigationInput[0] == "<":
        result = nav.visitNavigationMenu("-h", prevDir, navigationInput[1:])
        navigationOutput = 4 if result[0] == 0 else 1 if (result[0] == 1 or result[0] == 4) else navigationOutput #forward user input if history menu is empty and the user enters <[entry_nr] (result == 4)
    elif len(navigationInput) > 1 and navigationInput[0] == ">":
        navInput = navigationInput[1:]
        result = nav.visitNavigationMenu("-f", prevDir, navigationInput[1:])
        navigationOutput = 4 if result[0] == 0 else 1 if (result[0] == 1 or result[0] == 4) else navigationOutput #forward user input if favorites menu is empty and the user enters >[entry_nr] (result == 4)
    elif navigationInput == ",":
        result = nav.goTo(prevDir, os.getcwd())
        navigationOutput = 4 if result[0] == 0 else navigationOutput
    elif navigationInput == "+>":
        nav.addDirToFavorites()
        shouldForwardData = False
    elif navigationInput == "->":
        result = nav.removeDirFromFavorites()
        navigationOutput = 1 if result[0] == 1 else navigationOutput
    elif navigationInput == ":<>":
        nav.clearVisitedDirsMenu()
        shouldForwardData = False
    elif navigationInput == "!":
        shouldForwardData = False
        print("You exited navigation mode.")
    else:
        if navigationInput != "" and navigationInput[0] == ":":
            result = cmd.executeCommand(navigationInput[1:])
            navigationOutput = 2
        else:
            result = nav.goTo() if navigationInput == "" else nav.goTo(navigationInput, prevDir)
            navigationOutput = 4 if result[0] == 0 else navigationOutput
    if shouldForwardData == True:
        passedInput = result[1]
        passedOutput = result[2]
    return (navigationOutput, passedInput, passedOutput)

execute()