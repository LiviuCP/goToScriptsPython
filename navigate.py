import sys, os
import display as out
import navigation_goto as navgt
import nav_menus_update as nav
import command_goto as cgt
import cmd_menus_update as cmd
from os.path import expanduser

home_dir = expanduser("~") + "/"
input_storage_file = home_dir + ".store_input"
output_storage_file = home_dir + ".store_output"

def navigate():
    # initialize the environment, ensure the navigation and command history menus are sorted/consolidated
    nav.init()

    # ensure the input/output files exist (they will be removed later)
    with open(input_storage_file, "a") as input_storage:
        input_storage.write("")
    with open(input_storage_file, "a") as output_storage:
        output_storage.write("")

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
            with open(input_storage_file, "r") as input_storage:
                receivedInput = input_storage.readline().strip("\n")
            with open(output_storage_file, "r") as output_storage:
                receivedOutput = output_storage.readline().strip("\n")
            if result == 1:
                navigationInput = receivedInput
                forwardUserInput = True
            elif result == 2:
                prevCommand = receivedInput
                commandResult = receivedOutput
            elif result == 4:
                prevDir = receivedOutput

            if forwardUserInput == True:
                forwardUserInput = False
            else:
                break

        if navigationInput == "!":
            break

    return 0

# exit codes: 0 - no action performed (returned by default unless otherwise mentioned), 1 - forward input to BASH, 2 - update prevCommand and commandResult, 3 - no arguments, 4 - update prev dir and cd
def handleNavigationOption(navigationInput, prevDir, prevCommand):
    if navigationInput == "?":
        out.displayHelp()
    elif navigationInput == ":-":
        if prevCommand == "":
            print("No shell command previously executed")
        else:
            cmd.executeNewCommand(prevCommand)
    elif navigationInput == ":":
        result = cgt.editAndExecPrevCmd(prevCommand) if prevCommand != "" else cgt.editAndExecPrevCmd()
        if result == 0:
            return 2
    elif navigationInput == ":<":
        result = cgt.visitCommandMenu("--execute")
        # update in BASH ...
        if result == 0:
            return 2
        elif result == 1:
            return 1
    elif navigationInput == "::":
        result = cgt.visitCommandMenu("--edit")
        if result == 0:
            return 2
        elif result == 1:
            return 1
    elif navigationInput == "::<>":
        cmd.clearCommandHistory()
    elif navigationInput == "<":
        result = navgt.visitNavigationMenu("-h", prevDir)
        if result == 0:
            return 4
        elif result == 1:
            return 1
    elif navigationInput == ">":
        result = navgt.visitNavigationMenu("-f", prevDir)
        if result == 0:
            return 4
        elif result == 1:
            return 1
    elif len(navigationInput) > 1 and navigationInput[0] == "<":
        navInput = navigationInput[1:]
        result = navgt.visitNavigationMenu("-h", prevDir, navInput)
        if result == 0:
            return 4
        elif result == 1:
            return 1
    elif len(navigationInput) > 1 and navigationInput[0] == ">":
        navInput = navigationInput[1:]
        result = navgt.visitNavigationMenu("-f", prevDir, navInput)
        if result == 0:
            return 4
        elif result == 1:
            return 1
    elif navigationInput == ",":
        navgt.goTo(prevDir, os.getcwd())
        return 4
    elif navigationInput == "+>":
        nav.addToFavorites()
    elif navigationInput == "->":
        returnCode = nav.removeFromFavorites()
        if returnCode == 2:
            return 1
    elif navigationInput == ":<>":
        nav.clearHist()
    elif navigationInput == "!":
        print("You exited navigation mode.")
    else:
        if navigationInput != "" and navigationInput[0] == ":":
            commandToExecute = navigationInput[1:]
            with open(input_storage_file, "w") as input_storage:
                input_storage.write(commandToExecute) # will be taken over by BASH as prev command
            cmd.executeNewCommand(commandToExecute)
            return 2
        else:
            if navigationInput == "":
                navgt.goTo()
            else:
                navgt.goTo(navigationInput, prevDir)
            return 4

navigate()
