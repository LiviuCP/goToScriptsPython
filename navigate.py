import os
import display as out, navigation_goto as navgt, command_goto as cgt

def navigate():
    # initialize the environment, ensure the navigation and command history menus are sorted/consolidated
    navgt.initNavMenus()
    cgt.initCmdMenus()

    #initialize required variables
    prevDir = os.getcwd()
    prevCommand = ""
    commandResult = ""
    navigationInput = ""
    forwardUserInput = False

    # enter the directory navigation console
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
            result = handleNavigationOption(navigationInput, prevDir, prevCommand)
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

# return codes: 0 - no action performed (returned by default unless otherwise mentioned), 1 - forward input to BASH, 2 - update prevCommand and commandResult, 3 - no arguments, 4 - update prev dir and cd
def handleNavigationOption(navigationInput, prevDir, prevCommand):
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
            result = cgt.executeNewCommand(prevCommand)
    elif navigationInput == ":":
        result = cgt.editAndExecPrevCmd(prevCommand) if prevCommand != "" else cgt.editAndExecPrevCmd()
        if result[0] == 0:
            navigationOutput = 2
    elif navigationInput == ":<":
        result = cgt.visitCommandMenu("--execute")
        if result[0] == 0:
            navigationOutput = 2
        elif result[0] == 1:
            navigationOutput = 1
    elif navigationInput == "::":
        result = cgt.visitCommandMenu("--edit")
        if result[0] == 0:
            navigationOutput = 2
        elif result[0] == 1:
            navigationOutput = 1
    elif navigationInput == "::<>":
        cgt.clearCommandHistory()
        shouldForwardData = False
    elif navigationInput == "<":
        result = navgt.visitNavigationMenu("-h", prevDir)
        if result[0] == 0:
            navigationOutput = 4
        elif result[0] == 1:
            navigationOutput = 1
    elif navigationInput == ">":
        result = navgt.visitNavigationMenu("-f", prevDir)
        if result[0] == 0:
            navigationOutput = 4
        elif result[0] == 1:
            navigationOutput = 1
    elif len(navigationInput) > 1 and navigationInput[0] == "<":
        result = navgt.visitNavigationMenu("-h", prevDir, navigationInput[1:])
        if result[0] == 0:
            navigationOutput = 4
        elif result[0] == 1 or result[0] == 4: #forward user input if history menu is empty and the user enters <[entry_nr] (result == 4)
            navigationOutput = 1
    elif len(navigationInput) > 1 and navigationInput[0] == ">":
        navInput = navigationInput[1:]
        result = navgt.visitNavigationMenu("-f", prevDir, navigationInput[1:])
        if result[0] == 0:
            navigationOutput = 4
        elif result[0] == 1 or result[0] == 4: #forward user input if favorites menu is empty and the user enters <[entry_nr] (result == 4)
            navigationOutput = 1
    elif navigationInput == ",":
        result = navgt.goTo(prevDir, os.getcwd()) # have it updated, return available
        navigationOutput = 4
    elif navigationInput == "+>":
        navgt.addDirToFavorites()
        shouldForwardData = False
    elif navigationInput == "->":
        result = navgt.removeDirFromFavorites()
        if result[0] == 2:
            navigationOutput = 1
    elif navigationInput == ":<>":
        navgt.clearVisitedDirsMenu()
        shouldForwardData = False
    elif navigationInput == "!":
        shouldForwardData = False
        print("You exited navigation mode.")
    else:
        if navigationInput != "" and navigationInput[0] == ":":
            result = cgt.executeNewCommand(navigationInput[1:])
            navigationOutput = 2
        else:
            result = navgt.goTo() if navigationInput == "" else navgt.goTo(navigationInput, prevDir)
            navigationOutput = 4

    if shouldForwardData == True:
        passedInput = result[1]
        passedOutput = result[2]

    return (navigationOutput, passedInput, passedOutput)

navigate()
