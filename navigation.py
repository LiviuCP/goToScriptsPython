import sys, os, readline
import common, navigation_backend as nav
from os.path import isdir

""" core function for visiting directories """
def goTo(gtDirectory, prevDirectory):
    status = -1
    prevDir = os.getcwd()
    goToCommand = nav.buildGoToCommand(gtDirectory)
    os.system(goToCommand)
    currentDir = nav.getCurrentDirPath()
    if len(currentDir) > 0 and not common.hasPathInvalidCharacters(currentDir): # even if the directory is valid we should ensure it does not have characters like backslash (might cause undefined behavior)
        status = 0
        os.chdir(currentDir)
        if (prevDir != currentDir):
            print("Switched to new directory: " + currentDir)
            nav.updateNavigationHistory(currentDir)
            nav.consolidateHistory()
        else:
            print("Current directory remains unchanged: " + currentDir)
            prevDir = prevDirectory
    if not status is 0:
        prevDir = prevDirectory # ensure the previously visited dir stays the same for consistency reasons (not actually used if the goTo execution is not successful)
        print("Error when attempting to change directory! Possible causes: ")
        print(" - chosen directory path does not exist or has been deleted")
        print(" - chosen path is not a directory or the name has invalid characters")
        print(" - insufficient access rights")
        print(" - exception raised")
        print("Please try again!")
    return(status, "", prevDir)

""" navigation menu functions """
def initNavMenus():
    nav.initNavMenus()

# negative statuses are special statuses and will be retrieved in conjunction with special characters preceding valid entry numbers (like + -> status -1); path is forwarded as input and used by main app
def executeGoToFromMenu(menuChoice, previousDir, userInput = "", previousCommand = ""):
    assert menuChoice in ["-f", "-ff", "-h", "-fh"], "Invalid menuChoice argument"
    menuVisitResult = visitNavigationMenu(menuChoice, userInput, previousCommand)
    status = 0 # default status, normal execution or missing dir successful removal/mapping
    passedInput = ""
    passedOutput = previousDir
    dirPath = menuVisitResult[0]
    menuName = "favorites" if menuChoice == "-f" else "history" if menuChoice == "-h" else "filtered history" if menuChoice == "-fh" else "filtered favorites"
    if dirPath in [":1", ":4"]:
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
                elif menuChoice == "-ff": #entries from filtered favorites are actually part of favorites so they should be handled as a missing favorites entry case
                    menuChoice = "-f"
                handleResult = handleMissingDir(dirPath, menuChoice, previousDir)
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
            goToResult = goTo(dirPath, previousDir)
            status = goToResult[0]
            passedInput = goToResult[1]
            passedOutput = goToResult[2]
    else:
        status = 3
        passedInput = ""
        passedOutput = ""
    return (status, passedInput, passedOutput)

def visitNavigationMenu(menuChoice, userInput = "", previousCommand = ""):
    def displayHistMenu():
        nav.consolidateHistory() #normally this would not be required; nevertheless it's needed in order to fix a bug that appears both on Linux and Mac (persistent history entries vanish in specific circumstances - on Linux after executing a command, on Mac after opening a new Terminal Window); the fix is not 100% satisfactory yet it's the best that could be found so far
        print("VISITED DIRECTORIES")
        print("")
        print("-- RECENTLY VISITED --")
        print("")
        nav.displayFormattedRecentHistContent()
        print("")
        print("-- MOST VISITED --")
        print("")
        nav.displayFormattedPersistentHistContent()
    def displayFavoritesMenu():
        print("FAVORITE DIRECTORIES")
        print("")
        nav.displayFormattedFavoritesContent()
    def displayFilteredMenu(choice, content, totalNrOfMatches):
        assert choice in ["-fh", "-ff"]
        print("FILTERED VISITED DIRECTORIES") if choice == "-fh" else print("FILTERED FAVORITE DIRECTORIES")
        print("")
        nav.displayFormattedFilteredContent(content, totalNrOfMatches)
    def displayPageFooter(choice, filterKey = ""):
        toggleDict = {"-h" : "FAVORITE DIRECTORIES", "-f" : "VISITED DIRECTORIES", "-fh" : "FILTERED FAVORITE DIRECTORIES", "-ff" : "FILTERED VISITED DIRECTORIES"}
        print("")
        print("Current directory: " + os.getcwd())
        print("Last executed shell command: ", end='')
        print(previousCommand) if len(previousCommand) > 0 else print("none")
        print("")
        if len(filterKey) > 0:
            print("Applied filter: " + filterKey)
            print("")
        print("Enter the number of the directory you want to navigate to. ", end='')
        print("To navigate to parent directory enter character ',' before the number.")
        print("To set the directory as target dir enter '+' before the number. ", end='')
        print("Enter '-' to set its parent as target.")
        print("")
        print("Enter :t to toggle to " + toggleDict[choice] + ".")
        print("")
        print("Enter ! to quit.")
        print("")
    assert menuChoice in ["-f", "-ff", "-h", "-fh"], "Wrong menu option provided"
    filteredEntries = []
    if menuChoice in ["-fh", "-ff"]:
        assert len(userInput) > 0, "No filter has been provided for filtered navigation menu"
        filterResult = nav.buildFilteredNavigationHistory(filteredEntries, userInput) if menuChoice == "-fh" else nav.buildFilteredFavorites(filteredEntries, userInput)
        totalNrOfMatches = filterResult[0]
        appliedFilterKey = filterResult[1]
        userInput = "" #input should be reset to correctly account for the case when the resulting filtered history menu is empty
        os.system("clear")
        if len(filteredEntries) > 0:
            displayFilteredMenu(menuChoice, filteredEntries, totalNrOfMatches)
            displayPageFooter(menuChoice, appliedFilterKey)
            userInput = input()
            os.system("clear")
    elif len(userInput) == 0:
        os.system("clear")
        if not nav.isMenuEmpty(menuChoice):
            displayHistMenu() if menuChoice == "-h" else displayFavoritesMenu()
            displayPageFooter(menuChoice)
            userInput = input()
            os.system("clear")
    choiceResult = nav.choosePath(menuChoice, userInput, filteredEntries)
    return choiceResult

"""
The status returned by this method can have following values:
0 - mapping or removal attempted by user
1 - user input to be forwarded as regular input (dir path or command string)
2 - user exited the choose path dialog, returned to navigation mode
3 - invalid or missing arguments
4 - replacing directory to which mapping is requested does not exist
"""
def handleMissingDir(path, menu, previousDir):
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
        print("")
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
            replacingDirPath = nav.getReplacingDirPath(replacingDir)
            if replacingDirPath != ":4":
                prevDir = os.getcwd() # prev dir to be updated to current dir in case of successful mapping
                mappingResult = nav.mapMissingDir(missingDirPath, replacingDirPath)
                os.system("clear")
                print("Missing directory: " + mappingResult[0])
                print("Replacing directory: " + mappingResult[1])
                print("")
                print("Mapping performed successfully, navigating to replacing directory ...")
                print("")
                goTo(mappingResult[1], prevDir)
            else:
                status = 4
                os.system("clear")
                print("The chosen replacing directory (" + replacingDir + ") does not exist, has been deleted, you might not have the required access level or an internal error occurred.")
                print("Cannot perform mapping.")
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
