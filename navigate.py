import sys, os
import init
import handle_navigation_option as handle_nav
import display_general_navigation_output as display_out
from os.path import expanduser

home_dir = expanduser("~") + "/"
input_storage_file = home_dir + ".store_input"
output_storage_file = home_dir + ".store_output"

def navigate():
    # initialize the environment, ensure the navigation and command history menus are sorted/consolidated
    init.init()

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
                display_out.displayNavOutput()
            else:
                display_out.displayNavOutput(prevCommand, commandResult)

        navigationInput = input()

        while True == True:
            os.system("clear")
            result = handle_nav.handle_nav_option(navigationInput, prevDir, prevCommand)
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

navigate()
