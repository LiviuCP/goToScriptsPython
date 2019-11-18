import sys, os
import nav_menus_update as nav
import handle_missing_dir as hmdir
import go_to_dir as gtdir
from os.path import expanduser, isdir

home_dir = expanduser("~") + "/"
input_storage_file = home_dir + ".store_input"
output_storage_file = home_dir + ".store_output"

# to be solved: multiple return points!!!
def visit_nav_menu(menuChoice = "", previousDir = "", userInput = ""):
    if menuChoice == "" or previousDir == "":
        print("Insufficient number of arguments")
        return 3
    elif userInput == "":
        prevDir = previousDir
        dirPath = nav.choosePath(menuChoice)
    else:
        prevDir = previousDir
        dirPath = nav.choosePath(menuChoice, userInput)
    if dirPath == ":1":
        return 1 #forward user input
    elif dirPath == ":2":
        return 2
    elif dirPath == ":4":
        return 4
    elif dirPath != ":3":
        if not os.path.isdir(dirPath):
            result = hmdir.handleMissingDir(dirPath, menuChoice)
            if result == ":1":
                return 1 #forward user input
        else:
            gtdir.goTo(dirPath, prevDir)
            return 0
