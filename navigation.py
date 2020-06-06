import sys, os, readline
import common, navigation_backend as nav
from os.path import expanduser, isdir

home_dir = expanduser("~") + "/"
input_storage_file = home_dir + ".store_input"
output_storage_file = home_dir + ".store_output"

""" core functions for visiting directories and Finder synchronization """
def goTo(gtDirectory, prevDirectory, syncWithFinder):
    status = -1
    prevDir = os.getcwd()
    directory = home_dir if len(gtDirectory) == 0 else gtDirectory
    # build and execute command
    getDir = "directory=`echo " + directory + "`;" #if wildcards are being used the full dir name should be expanded
    cdCommand = "cd " + '\"' + "$directory" + '\"' + " 2> /dev/null;"
    executionStatus = "echo $? > " + output_storage_file + ";"
    writeCurrentDir = "pwd > " + input_storage_file + ";"
    executeCommandWithStatus = getDir + "\n" + cdCommand + "\n" + executionStatus + "\n" + writeCurrentDir
    os.system(executeCommandWithStatus)
    # read command exit code and create the status message
    with open(output_storage_file, "r") as outputStorage:
        if outputStorage.readline().strip('\n') == "0":
            with open(input_storage_file, "r") as inputStorage:
                currentDir = inputStorage.readline().strip('\n')
                if not common.hasPathInvalidCharacters(currentDir): # even if the directory is valid we should ensure it does not have characters like backslash (might cause undefined behavior)
                    status = 0
                    os.chdir(currentDir)
                    if (prevDir != currentDir):
                        print("Switched to new directory: " + currentDir)
                        nav.updateHistory(currentDir)
                        nav.consolidateHistory()
                    else:
                        print("Current directory remains unchanged: " + currentDir)
                        prevDir = prevDirectory
                    # update current directory in Finder if sync enabled
                    if syncWithFinder == True:
                        doFinderSync()
        if not status is 0:
            prevDir = prevDirectory # ensure the previously visited dir stays the same for consistency reasons (not actually used if the goTo execution is not successful)
            print("Error when attempting to change directory! Possible causes: ")
            print(" - chosen directory path does not exist or has been deleted")
            print(" - chosen path is not a directory or the name has invalid characters")
            print(" - insufficient access rights")
            print(" - exception raised")
            print("Please try again!")
    return(status, "", prevDir)

def doFinderSync():
    setDelays = "delayBeforeClose=0.1;" + "\n" + "delayBeforeReopen=0.2" + "\n" + "delayAfterReopen=0.5;" + "\n" + "delayErrorReopen=1.8;" + "\n"
    closeFinder = "sleep $delayBeforeClose;" + "\n" + "osascript -e \'quit app \"Finder\"\';" + "\n"
    handleClosingError = "if [[ $? != 0 ]]; then echo \'An error occured when closing Finder\'; " + "\n"
    reopenFinder = "else sleep $delayBeforeReopen; open . 2> /dev/null;" + "\n"
    handleReopeningError = "if [[ $? != 0 ]]; then sleep $delayErrorReopen; echo \'An error occured when opening the new directory in Finder\'; " + "\n"
    addDelayAfterSuccessfulReopen = "else sleep $delayAfterReopen;" + "\n" + "fi" + "\n" + "fi" + "\n"
    openTerminal = "open -a terminal;"
    updateFinder = setDelays + closeFinder + handleClosingError + reopenFinder + handleReopeningError + addDelayAfterSuccessfulReopen + openTerminal
    os.system(updateFinder)

def doCloseFinder():
    setDelays = "delayBeforeClose=0.1;" + "\n"
    closeFinder = "sleep $delayBeforeClose;" + "\n" + "osascript -e \'quit app \"Finder\"\';" + "\n"
    handleClosingError = "if [[ $? != 0 ]]; then echo \'An error occured when closing Finder\'; " + "\n" + "fi"
    updateFinder = setDelays + closeFinder + handleClosingError
    os.system(updateFinder)

""" navigation menu functions """
def initNavMenus():
    nav.initNavMenus()

# negative statuses are special statuses and will be retrieved in conjunction with special characters preceding valid entry numbers (like + -> status -1); path is forwarded as input and used by main app
def executeGoToFromMenu(menuChoice, previousDir, syncWithFinder, userInput = ""):
    assert menuChoice in ["-f", "-h", "-fh"], "Invalid menuChoice argument"
    menuVisitResult = visitNavigationMenu(menuChoice, userInput)
    status = 0 # default status, normal execution or missing dir successful removal/mapping
    passedInput = ""
    passedOutput = previousDir
    dirPath = menuVisitResult[0]
    menuName = "favorites" if menuChoice == "-f" else "history" if menuChoice == "-h" else "filtered history"
    if dirPath == ":1" or dirPath == ":4":
        status = int(dirPath[1])
        passedInput = menuVisitResult[1]
        if dirPath == ":4":
            print("There are no entries in the " + menuName + " menu.")
    elif dirPath == ":2":
        status = int(dirPath[1])
        print("You exited the " + menuName + " menu!")
    elif dirPath != ":3":
        if not os.path.isdir(dirPath):
            if menuVisitResult[1] == ":parent" or menuVisitResult[1] == ":preceding-":
                print("Invalid parent directory path: " + dirPath)
                print("The directory might have been moved, renamed or deleted.")
                print()
                print("Please remove or map the directory and/or child directories within history and/or favorites menus.")
            else:
                if menuChoice == "-fh": #entries from filtered history are actually part of persistent history so they should be handled as a missing persistent history entry case
                    menuChoice = "-h"
                handleResult = handleMissingDir(dirPath, menuChoice, previousDir, syncWithFinder)
                if handleResult[0] == 1:
                    status = 1 #forward user input
                    passedInput = handleResult[1]
                    passedOutput = handleResult[2]
                elif handleResult[0] == 0:
                    passedOutput = handleResult[2] # previous directory in case mapping was successful
        elif menuVisitResult[1] == ":preceding+" or menuVisitResult[1] == ":preceding-":
            status = -1
            passedInput = dirPath
        else:
            goToResult = goTo(dirPath, previousDir, syncWithFinder)
            status = goToResult[0]
            passedInput = goToResult[1]
            passedOutput = goToResult[2]
    else:
        status = 3
        passedInput = ""
        passedOutput = ""
    return (status, passedInput, passedOutput)

def visitNavigationMenu(menuChoice, userInput = ""):
    def displayCommonMenuPart():
        print("")
        print("Current directory: " + os.getcwd())
        print("")
        print("Enter the number of the directory you want to navigate to. ", end='')
        print("To navigate to parent directory enter character ',' before the number.")
        print("To set the directory as target dir enter '+' before the number. ", end='')
        print("Enter '-' to set its parent as target.")
        print("")
        print("Enter ! to quit.")
        print("")
    def displayHistMenu():
        print("VISITED DIRECTORIES")
        print("")
        print("-- RECENTLY VISITED --")
        print("")
        nav.displayFormattedRecentHistContent()
        print("")
        print("-- MOST VISITED --")
        print("")
        nav.displayFormattedPersistentHistContent()
        displayCommonMenuPart()
    def displayFilteredHistMenu(content, totalNrOfMatches):
        print("FILTERED VISITED DIRECTORIES")
        print("")
        nav.displayFormattedFilteredHistContent(content, totalNrOfMatches)
        displayCommonMenuPart()
    def displayFavoritesMenu():
        print("FAVORITE DIRECTORIES")
        print("")
        nav.displayFormattedFavoritesContent()
        displayCommonMenuPart()
    assert menuChoice in ["-f", "-h", "-fh"], "Wrong menu option provided"
    filteredHistEntries = []
    if menuChoice == "-fh":
        assert len(userInput) > 0, "No filter has been provided for filtered navigation history"
        totalNrOfMatches = nav.buildFilteredHistory(filteredHistEntries, userInput)
        userInput = "" #input should be reset to correctly account for the case when the resulting filtered history menu is empty
        os.system("clear")
        if len(filteredHistEntries) > 0:
            displayFilteredHistMenu(filteredHistEntries, totalNrOfMatches)
            userInput = input()
            os.system("clear")
    elif len(userInput) == 0:
        os.system("clear")
        if not nav.isMenuEmpty(menuChoice):
            displayHistMenu() if menuChoice == "-h" else displayFavoritesMenu()
            userInput = input()
            os.system("clear")
    choiceResult = nav.choosePath(menuChoice, userInput, filteredHistEntries)
    return choiceResult

"""
The status returned by this method can have following values:
0 - mapping or removal attempted by user
1 - user input to be forwarded as regular input (dir path or command string)
2 - user exited the choose path dialog, returned to navigation mode
3 - invalid or missing arguments
4 - replacing directory to which mapping is requested does not exist
"""
def handleMissingDir(path, menu, previousDir, syncWithFinder):
    assert len(path) > 0, "Empty 'missing path' argument detected"
    assert menu in ["-h", "-f"], "Invalid menu type option passed as argument"
    status = 0 # default status, successful missing directory path mapping or removal
    prevDir = previousDir # keep actual previous dir information in case remove dir from menu is executed (otherwise it will be lost)
    missingDirPath = path
    menuType = "history" if menu == "-h" else "favorites"
    os.system("clear")
    print("Invalid directory path: " + missingDirPath)
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
    # map missing directory to a valid replacing dir
    elif userChoice == "!m":
        doMapping = True
        os.system("clear")
        print("Missing directory: " + missingDirPath)
        print("")
        print("Enter the name and/or path of the replacing directory.")
        print("Enter < for mapping from history menu and > for mapping from favorites.")
        print("Enter ! to quit mapping.")
        replacingDir = input()
        if replacingDir == "<" or replacingDir == ">":
            menuName = "history" if replacingDir == "<" else "favorites"
            menuVisitResult = visitNavigationMenu("-h" if replacingDir == "<" else "-f")
            if menuVisitResult[0] == ":4":
                status = 4
                doMapping = False
                print("There are no entries in the " + menuName + " menu. Cannot perform mapping.")
            elif menuVisitResult[0] == ":2":
                status = 2
                doMapping = False
                print("Mapping aborted.")
            elif menuVisitResult[0] == ":1":
                replacingDir = menuVisitResult[1] #input mirrored back, "normal" input interpreted as user entered path
            else:
                replacingDir = menuVisitResult[0] #path retrieved from menu
        elif replacingDir == "!":
            status = 2
            doMapping = False
            os.system("clear")
            print("Mapping aborted.")
        if doMapping == True:
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
                        status = 4
                        os.system("clear")
                        print("The chosen replacing directory (" + replacingDir + ") does not exist, has been deleted or you might not have the required access level.")
                        print("Cannot perform mapping.")
                    else:
                        prevDir = os.getcwd() # prev dir to be updated to current dir in case of successful mapping
                        mappingResult = nav.mapMissingDir(missingDirPath, replacingDirPath)
                        os.system("clear")
                        print("Missing directory: " + mappingResult[0])
                        print("Replacing directory: " + mappingResult[1])
                        print("")
                        print("Mapping performed successfully, navigating to replacing directory ...")
                        print("")
                        goTo(mappingResult[1], prevDir, syncWithFinder)
    elif userChoice == "!":
        status = 2
        os.system("clear")
        print("You exited the " + menuType +  " menu")
    else:
        status = 1
    return (status, userChoice, prevDir)

def clearVisitedDirsMenu():
    nav.clearHistory()
    print("Content of navigation history menu has been erased.")

def addDirToFavorites(dirPath = ""):
    pathToAdd = common.getAbsoluteDirPath(dirPath)
    if len(pathToAdd) > 0:
        if not nav.isContainedInFavorites(pathToAdd):
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
    status = 0 # default status, successful removal or aborted by user
    userInput = ""
    if nav.isFavEmpty():
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
