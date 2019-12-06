import sys, os
import common, navigation_backend as nav
from os.path import expanduser, isdir

home_dir = expanduser("~") + "/"
input_storage_file = home_dir + ".store_input"
output_storage_file = home_dir + ".store_output"

""" core function for visiting directories """
def goTo(gtDirectory = "", prevDirectory = ""):
    status = 0 #default status, successful execution
    prevDir = os.getcwd()
    directory = home_dir if gtDirectory == "" else gtDirectory
    # build and execute command
    getDir = "directory=`echo " + directory + "`;" #if wildcards are being used the full dir name should be expanded
    sourceCommand = "source ~/.bashrc;" #include .bashrc to ensure the aliases and scripts work
    executionStatus = "echo $? > " + output_storage_file + ";"
    cdCommand = "cd " + '\"' + "$directory" + '\"' + " 2> /dev/null;"
    writeCurrentDir = "pwd > " + input_storage_file + ";"
    executeCommandWithStatus = getDir + "\n" + sourceCommand + "\n" + cdCommand + "\n" + executionStatus + "\n" + writeCurrentDir
    os.system(executeCommandWithStatus)
    # read command exit code and create the status message
    with open(output_storage_file, "r") as outputStorage:
        success = True if outputStorage.readline().strip('\n') == "0" else False
        if success == True:
            with open(input_storage_file, "r") as inputStorage:
                currentDir = inputStorage.readline().strip('\n')
                os.chdir(currentDir)
                print("Previous directory: " + prevDir)
                print("Current directory: " + currentDir)
                if (prevDir != currentDir):
                    nav.updateHistory(currentDir)
                    nav.consolidateHistory()
        else:
            status = -1 # unsuccessful goTo, cannot change dir
            prevDir = prevDirectory # ensure the previously visited dir stays the same for consistency reasons (not actually used if the goTo execution is not successful)
            print("Error when attempting to change directory! Possible causes: ")
            print(" - chosen directory path does not exist or has been deleted")
            print(" - chosen path is not a directory")
            print(" - insufficient access rights")
            print("Please try again!")
        return(status, "", prevDir)

""" navigation menu functions """
def initNavMenus():
    nav.initNavMenus()

def visitNavigationMenu(menuChoice = "", previousDir = "", userInput = ""):
    def displayHistMenu():
        print("VISITED DIRECTORIES")
        print("")
        print("-- RECENTLY VISITED --")
        print("")
        nav.displayFormattedRecentHistContent()
        print("")
        print("--  MOST VISITED --")
        print("")
        nav.displayFormattedPersistentHistContent()
        print("")
        print("Current directory: " + os.getcwd())
        print("")
        print("Enter the number of the directory you want to navigate to.")
        print("Enter ! to quit.")
        print("")
    def displayFavoritesMenu():
        print("FAVORITE DIRECTORIES")
        print("")
        nav.displayFormattedFavoritesContent()
        print("")
        print("Current directory: " + os.getcwd())
        print("")
        print("Enter the number of the directory you want to navigate to.")
        print("Enter ! to quit.")
        print("")
    # *** actual function ***
    status = 0 # default status, normal execution or missing dir successful removal/mapping
    passedInput = ""
    passedOutput = previousDir
    if menuChoice == "" or previousDir == "":
        print("Insufficient number of arguments")
        status = 3
    else:
        prevDir = previousDir
        if menuChoice != "-f" and menuChoice != "-h":
            print("invalid argument provided, no menu selected")
            choiceResult = (":3", "", "")
        else:
            menuName = "favorites" if menuChoice == "-f" else "history"
            if userInput == "":
                os.system("clear")
                if nav.isMenuEmpty(menuChoice) == True:
                    print("There are no entries in the " + menuName + " menu.")
                else:
                    displayHistMenu() if menuChoice == "-h" else displayFavoritesMenu()
                    userInput = input() # to update: enable path autocomplete
                    os.system("clear")
            choiceResult = nav.choosePath(menuChoice, userInput)
    if status == 0:
        dirPath = choiceResult[0]
        if dirPath == ":1" or dirPath == ":4":
            status = int(dirPath[1])
            passedInput = choiceResult[1]
        elif dirPath == ":2":
            status = int(dirPath[1])
            print("You exited the " + menuName + " menu!")
        elif dirPath != ":3":
            if not os.path.isdir(dirPath):
                handleResult = handleMissingDir(dirPath, menuChoice)
                if handleResult[0] == 1:
                    status = 1 #forward user input
                    passedInput = handleResult[1]
                    passedOutput = handleResult[2]
            else:
                goToResult = goTo(dirPath, prevDir)
                status = goToResult[0]
                passedInput = goToResult[1]
                passedOutput = goToResult[2]
        else:
            status = 3
            passedInput = ""
            passedOutput = ""
    return (status, passedInput, passedOutput)

"""
The status returned by this method can have following values:
0 - mapping or removal attempted by user
1 - user input to be forwarded as regular input (dir path or command string)
2 - user exited the choose path dialog, returned to navigation mode
3 - invalid or missing arguments
4 - replacing directory to which mapping is requested does not exist
"""
def handleMissingDir(path, menu):
    # we need two arguments, one for missing directory path and second for menu type (history/favorites)
    if path == "" or menu not in ["-h", "-f"]:
        print("handleMissingDir: invalid arguments")
        status = 3
    else:
        missingDirPath = path
        menuType = "history" if menu == "-h" else "favorites"
        os.system("clear")
        print("Invalid path " + missingDirPath)
        print("The directory might have been moved, renamed or deleted.")
        print("")
        print("Please choose the required action: ")
        print("!r to remove the directory from the menus")
        print("!m to map to an existing directory")
        print("! to quit")
        print("")
        userChoice = input()
        # remove directory from history, don't map to anything
        if userChoice == "!r":
            removedPath = nav.removeMissingDir(missingDirPath)
            os.system("clear")
            print("Entry " + removedPath + " has been removed from the menus.")
            status = 0
        # map missing directory to a valid replacing dir
        elif userChoice == "!m":
            os.system("clear")
            print("Missing directory: " + missingDirPath)
            print("")
            print("Enter the name and/or path of the replacing directory.")
            replacingDir = input()
            with open(input_storage_file, "w") as inputStorage:
                inputStorage.write(replacingDir)
                inputStorage.close() # file needs to be closed otherwise the below executed BASH command might return unexpected results
                # build BASH command for retrieving the absolute path of the replacing dir (if exists)
                command = "input=`head -1 " + input_storage_file + "`; "
                command = command + "output=" + output_storage_file + "; "
                command = command + "cd $input 2> /dev/null; if [[ $? == 0  ]]; then pwd > \"$output\"; else echo :4 > \"$output\"; fi"
                os.system(command)
                with open(output_storage_file, "r") as outputStorage:
                    replacingDirPath = outputStorage.readline().strip('\n')
                    if replacingDirPath == ":4":
                        os.system("clear")
                        print("The chosen replacing directory (" + replacingDir + ") does not exist, has been deleted or you might not have the required access level.")
                        print("Cannot perform mapping.")
                    else:
                        mappingResult = nav.mapMissingDir(missingDirPath, replacingDirPath)
                        os.system("clear")
                        print("Missing directory: " + mappingResult[0])
                        print("Replacing directory: " + mappingResult[1])
                        print("")
                        print("Mapping performed successfully.")
                    status = 0
        elif userChoice == "!":
            os.system("clear")
            print("You exited the " + menuType +  " menu")
            status = 2
        else:
            status = 1
    return (status, userChoice, "")

def clearVisitedDirsMenu():
    nav.clearHist()
    print("Content of navigation history menu has been erased.")

def addDirToFavorites(dirPath = ""):
    pathToAdd = common.getAbsoluteDirPath(dirPath)
    if pathToAdd != "":
        if nav.isContainedInFavorites(pathToAdd) == False:
            nav.addPathToFavorites(pathToAdd)
            print("Directory " + pathToAdd + " added to favorites.")
        else:
            print("Directory " + pathToAdd + " already added to favorites.")
    else:
        os.system("clear")
        print("Directory " + dirPath + " does not exist, has been deleted or you might not have the required access level.")
        print("Cannot add to favorites.")

def removeDirFromFavorites():
    def displayFavoritesEntryRemovalDialog():
        print("REMOVE DIRECTORY FROM FAVORITES")
        print('')
        nav.displayFormattedFavoritesContent()
        print('')
        print("Current directory: " + os.getcwd())
        print('')
        print("Enter the number of the directory to be removed from favorites.")
        print("Enter ! to quit this dialog.")
        print('')
    # *** actual function ***
    status = 0 # default status, successful removal or aborted by user
    userInput = ""
    if nav.isFavEmpty() == True:
        print("There are no entries in the favorites menu.")
        status = 4
    else:
        displayFavoritesEntryRemovalDialog()
        userInput = input()
        os.system("clear")
        if nav.isValidInput(userInput):
            removedPath = nav.removePathFromFavorites(userInput)
            print("Entry " + removedPath + " removed from favorites menu.")
        elif userInput == '!':
            print("No entry removed from favorites menu.")
        else:
            status = 1 # forward user input as regular input
    return (status, userInput, "")
