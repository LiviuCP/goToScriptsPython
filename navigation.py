import os
import common, navigation_backend as nav, navigation_settings as navset, system_functionality as sysfunc, display as out
from pathlib import Path

class Navigation:
    def __init__(self, startingDirectory):
        self.previousDirectory = startingDirectory
        self.previousNavigationFilter = ""
        self.nav = nav.NavigationBackend()

    def getPreviousDirectory(self):
        return self.previousDirectory

    def getPreviousNavigationFilter(self):
        return self.previousNavigationFilter

    """ core function for visiting directories """
    def goTo(self, gtDirectory):
        status = -1
        syncedCurrentDir, fallbackPerformed = sysfunc.syncCurrentDir()
        assert not fallbackPerformed, "Current dir fallback not allowed"
        prevDir = syncedCurrentDir # current directory path (should become previous dir after goto)
        currentDir = common.getAbsoluteDirPath(gtDirectory) # target directory path (should become current directory after goto)
        if len(currentDir) > 0 and not common.hasPathInvalidCharacters(currentDir): # even if the directory is valid we should ensure it does not have characters like backslash (might cause undefined behavior)
            status = 0
            os.chdir(currentDir)
            if (prevDir != currentDir):
                print(f"Switched to new directory: {currentDir}")
                self.nav.updateHistory(currentDir)
                self.previousDirectory = prevDir
            else:
                print(f"Current directory remains unchanged: {currentDir}")
        if status != 0:
            print("Error when attempting to change directory! Possible causes: ")
            print(" - chosen directory path does not exist or has been deleted")
            print(" - chosen path is not a directory or the name has invalid characters")
            print(" - insufficient access rights")
            print(" - exception raised")
            print("Please try again!")
        return(status, "", "")

    """ Convenience method for visiting the previous directory """
    def goToPreviousDirectory(self):
        return self.goTo(self.previousDirectory)

    """ visit directory by choosing an entry from a navigation menu (history, favorites, filtered menus) """
    # negative statuses are special statuses and will be retrieved in conjunction with special characters preceding valid entry numbers (like + -> status -1); path is forwarded as input and used by main app
    def executeGoToFromMenu(self, menuChoice, userInput = "", previousCommand = ""):
        assert menuChoice in ["-f", "-ff", "-h", "-fh"], "Invalid menuChoice argument"
        dirPath, menuVisitPassedInput, menuVisitPassedOutput = self.__visitNavigationMenu__(menuChoice, userInput, previousCommand)
        status = 0 # default status, normal execution or missing dir successful removal/mapping
        passedInput = ""
        menuName = "favorites" if menuChoice == "-f" else "history" if menuChoice == "-h" else "filtered history" if menuChoice == "-fh" else "filtered favorites"
        syncedCurrentDir, fallbackPerformed = sysfunc.syncCurrentDir()
        if fallbackPerformed:
            out.printFallbackMessage()
        elif dirPath in [":1", ":4"]:
            status = int(dirPath[1])
            passedInput = menuVisitPassedInput
            if dirPath == ":4":
                print(f"There are no entries in the {menuName} menu.")
        elif dirPath == ":2":
            status = int(dirPath[1])
            print(f"You exited the {menuName} menu!")
        elif dirPath != ":3":
            if not os.path.isdir(dirPath):
                if menuVisitPassedInput in [":parent", ":preceding-"]:
                    print(f"Invalid parent directory path: {dirPath}")
                    print("The directory might have been moved, renamed or deleted.")
                    print()
                    print("Please remove or map the directory and/or child directories within history and/or favorites menus.")
                else:
                    if menuChoice == "-fh": #entries from filtered history are actually part of persistent history so they should be handled as a missing persistent history entry case
                        menuChoice = "-h"
                    elif menuChoice == "-ff": #entries from filtered favorites are actually part of favorites so they should be handled as a missing favorites entry case
                        menuChoice = "-f"
                    handleMissingDirStatus, handleMissingDirPassedInput, handleMissingDirPassedOutput = self.__handleMissingDir__(dirPath, menuChoice)
                    if handleMissingDirStatus == 1:
                        status = 1 #forward user input
                        passedInput = handleMissingDirPassedInput
            elif menuVisitPassedInput in [":preceding+", ":preceding-"]:
                status = -1
                passedInput = dirPath
            else:
                status, passedInput, passedGoToOutput = self.goTo(dirPath)
        else:
            status = 3
            passedInput = ""
        return (status, passedInput, "")

    """ resets the navigation history (including separate history for favorite directories) """
    def clearVisitedDirsMenu(self):
        self.nav.clearHistory()
        print("Content of navigation history menu has been erased.")

    """ adds directory to favorite paths """
    def addDirToFavorites(self, dirPath = ""):
        syncedCurrentDir, fallbackPerformed = sysfunc.syncCurrentDir()
        assert not fallbackPerformed, "Current directory fallback not allowed"
        if len(dirPath) == 0:
            pathToAdd = syncedCurrentDir
        else:
            pathToAdd = common.getAbsoluteDirPath(dirPath)
        if len(pathToAdd) > 0:
            pathAdded = self.nav.addPathToFavorites(pathToAdd)
            if pathAdded:
                print(f"Directory {pathToAdd} added to favorites.")
            else:
                print(f"Directory {pathToAdd} already added to favorites.")
        else:
            os.system("clear")
            print(f"Directory {dirPath} does not exist, has been deleted or you might not have the required access level.")
            print("Cannot add to favorites.")

    """ removes dir from favorite paths """
    def removeDirFromFavorites(self):
        def displayFavoritesEntryRemovalDialog(currentDir):
            print("REMOVE DIRECTORY FROM FAVORITES")
            print('')
            self.__displayFormattedNavFileContent__(self.nav.getFavoritesInfo())
            print('')
            print(f"Current directory: {currentDir}")
            print('')
            print("Enter the number of the directory to be removed from favorites.")
            print("Enter ! to quit this dialog.")
            print('')
        syncedCurrentDir, fallbackPerformed = sysfunc.syncCurrentDir()
        assert not fallbackPerformed, "Current dir fallback not allowed"
        status = 0 # default status, successful removal or aborted by user
        userInput = ""
        favorites = self.nav.getFavoritesInfo()
        if len(favorites) == 0:
            print("There are no entries in the favorites menu.")
            status = 4
        else:
            displayFavoritesEntryRemovalDialog(syncedCurrentDir)
            userInput = input()
            os.system("clear")
            if userInput == '!':
                print("No entry removed from favorites menu.")
            else:
                pathToRemove = common.getMenuEntry(favorites, userInput)
                if pathToRemove is not None:
                    pathRemoved = self.nav.removePathFromFavorites(pathToRemove)
                    if pathRemoved:
                        print(f"Entry {pathToRemove} removed from favorites menu.")
                    else:
                        print(f"Error! Entry {pathToRemove} could not be removed from favorites menu.")
                else:
                    status = 1 # forward user input as regular input
        return (status, userInput, "")

    """ used for quick favorite directories access """
    def isValidFavoritesEntryNr(self, userInput):
        return common.isValidMenuEntryNr(userInput, self.nav.getFavoritesInfo())

    """ quick navigation history is part of recent history but can be accessed outside the regular history menus """
    def displayQuickNavigationHistory(self):
        (consolidatedHistory, recentHistoryEntriesCount) = self.nav.getHistoryInfo()
        recentHistory = consolidatedHistory[0: recentHistoryEntriesCount]
        self.__displayFormattedNavFileContent__(recentHistory, 0, navset.q_hist_max_entries)

    """ checks the entry number is a positive integer belonging to the range of entries contained in quick history (subset of recent navigation history) """
    def isValidQuickNavHistoryEntryNr(self, userInput):
        return self.nav.isValidQuickHistoryEntryNr(userInput)

    """ requests closing the navigation functionality in an orderly manner when application gets closed """
    def closeNavigation(self):
        return self.nav.close()

    """
    The status returned by this method can have following values:
    0 - mapping or removal attempted by user
    1 - user input to be forwarded as regular input (dir path or command string)
    2 - user exited the choose path dialog, returned to navigation mode
    3 - invalid or missing arguments
    4 - replacing directory to which mapping is requested does not exist
    """
    def __handleMissingDir__(self, path, menu):
        syncedCurrentDir, fallbackPerformed = sysfunc.syncCurrentDir()
        assert not fallbackPerformed, "Current dir fallback not allowed"
        assert len(path) > 0, "Empty 'missing path' argument detected"
        assert menu in ["-h", "-f"], "Invalid menu type option passed as argument"
        status = 0 # default status, successful missing directory path mapping or removal
        missingDirPath = path
        menuType = "history" if menu == "-h" else "favorites"
        os.system("clear")
        print(f"Invalid directory path: {missingDirPath}")
        print("The directory might have been moved, renamed or deleted.")
        print("")
        print("Please choose the required action: ")
        print("!r to remove the directory from the menus")
        print("!m to map to an existing directory")
        print("! to quit")
        print("")
        userChoice = input()
        syncedCurrentDir, fallbackPerformed = sysfunc.syncCurrentDir() # handle the situation when current directory became inaccessible right before the user entered the choice
        if fallbackPerformed:
            out.printFallbackMessage()
        # remove directory from history, don't map to anything
        elif userChoice == "!r":
            removedPath = self.nav.removeMissingDir(missingDirPath)
            os.system("clear")
            print(f"Entry {removedPath} has been removed from the menus.")
        # map missing directory to a valid replacing dir
        elif userChoice == "!m":
            doMapping = True
            os.system("clear")
            print(f"Missing directory: {missingDirPath}")
            print("")
            print("Enter the name and/or path of the replacing directory.")
            print("Enter < for mapping from history menu and > for mapping from favorites.")
            print("Enter ! to quit mapping.")
            print("")
            replacingDir = input()
            syncedCurrentDir, fallbackPerformed = sysfunc.syncCurrentDir() # handle the situation when current directory became inaccessible during the mapping process before user entered any mapping input
            if fallbackPerformed:
                doMapping = False
                out.printFallbackMessage()
            elif replacingDir == "<" or replacingDir == ">":
                menuName = "history" if replacingDir == "<" else "favorites"
                dirPath, menuVisitPassedInput, menuVisitPassedOutput = self.__visitNavigationMenu__("-h" if replacingDir == "<" else "-f")
                syncedCurrentDir, fallbackPerformed = sysfunc.syncCurrentDir() # handle the situation when current directory became inaccessible during the mapping process while in history/favorites menu
                if fallbackPerformed:
                    doMapping = False
                    out.printFallbackMessage()
                elif dirPath == ":4":
                    status = 4
                    doMapping = False
                    print(f"There are no entries in the {menuName} menu. Cannot perform mapping.")
                elif dirPath == ":2":
                    status = 2
                    doMapping = False
                    print("Mapping aborted.")
                elif dirPath == ":1":
                    replacingDir = menuVisitPassedInput #input mirrored back, "normal" input interpreted as user entered path
                else:
                    replacingDir = dirPath #path retrieved from menu
            elif replacingDir == "!":
                status = 2
                doMapping = False
                os.system("clear")
                print("Mapping aborted.")
            if doMapping == True:
                replacingDirPath = common.getAbsoluteDirPath(replacingDir)
                if len(replacingDirPath) > 0:
                    self.previousDirectory = syncedCurrentDir # prev dir to be updated to current dir in case of successful mapping
                    replacedPath, replacingPath = self.nav.mapMissingDir(missingDirPath, replacingDirPath)
                    os.system("clear")
                    print(f"Missing directory: {replacedPath}")
                    print(f"Replacing directory: {replacingPath}")
                    print("")
                    print("Mapping performed successfully, navigating to replacing directory ...")
                    print("")
                    self.goTo(replacingPath)
                else:
                    status = 4 # replacingDirPath == ":4"
                    os.system("clear")
                    print(f"The chosen replacing directory ({replacingDir}) does not exist, has been deleted, you might not have the required access level or an internal error occurred.")
                    print("Cannot perform mapping.")
        elif userChoice == "!":
            status = 2
            os.system("clear")
            print(f"You exited the {menuType} menu")
        else:
            status = 1
        return (status, userChoice, "")

    """ Displays the requested navigation menu and prompts the user to enter the required option """
    def __visitNavigationMenu__(self, menuChoice, userInput = "", previousCommand = ""):
        def displayHistMenu():
            (consolidatedHistory, recentHistoryEntriesCount) = self.nav.getHistoryInfo()
            print("VISITED DIRECTORIES")
            print("")
            print("-- RECENTLY VISITED --")
            print("")
            self.__displayFormattedNavFileContent__(consolidatedHistory, 0, recentHistoryEntriesCount)
            print("")
            print("-- MOST VISITED --")
            print("")
            self.__displayFormattedNavFileContent__(consolidatedHistory, recentHistoryEntriesCount)
        def displayFavoritesMenu():
            print("FAVORITE DIRECTORIES")
            print("")
            self.__displayFormattedNavFileContent__(self.nav.getFavoritesInfo())
        def displayFilteredMenu(choice, filteredContent, totalNrOfMatches):
            assert choice in ["-fh", "-ff"]
            print("FILTERED VISITED DIRECTORIES") if choice == "-fh" else print("FILTERED FAVORITE DIRECTORIES")
            print("")
            self.__displayFormattedNavFileContent__(filteredContent, 0)
            print("")
            print(f"\tThe search returned {str(totalNrOfMatches)} match(es).")
            if totalNrOfMatches > len(filteredContent):
                print("\tFor better visibility only part of them are displayed. Please narrow the search if needed.")
        def displayPageFooter(currentDir, choice, filterKey = ""):
            toggleDict = {"-h" : "FAVORITE DIRECTORIES", "-f" : "VISITED DIRECTORIES", "-fh" : "FILTERED FAVORITE DIRECTORIES", "-ff" : "FILTERED VISITED DIRECTORIES"}
            print("")
            print(f"Current directory: {currentDir}")
            print("Last executed shell command: ", end='')
            print(previousCommand) if len(previousCommand) > 0 else print("none")
            print("")
            if len(filterKey) > 0:
                print(f"Applied filter: {filterKey}")
                print("")
            print("Enter the number of the directory you want to navigate to. ", end='')
            print("To navigate to parent directory enter character ',' before the number.")
            print("To set the directory as target dir enter '+' before the number. ", end='')
            print("Enter '-' to set its parent as target.")
            print("")
            print(f"Enter :t to toggle to {toggleDict[choice]}.")
            print("")
            print("Enter ! to quit.")
            print("")
        syncedCurrentDir, fallbackPerformed = sysfunc.syncCurrentDir()
        assert not fallbackPerformed, "Current dir fallback not allowed"
        assert menuChoice in ["-f", "-ff", "-h", "-fh"], "Wrong menu option provided"
        filteredEntries = []
        if menuChoice in ["-fh", "-ff"]:
            assert len(userInput) > 0, "No filter has been provided for filtered navigation menu"
            self.previousNavigationFilter = userInput
            totalNrOfMatches, appliedFilterKey = self.nav.buildFilteredHistory(userInput, filteredEntries) if menuChoice == "-fh" else self.nav.buildFilteredFavorites(userInput, filteredEntries)
            userInput = "" #input should be reset to correctly account for the case when the resulting filtered history menu is empty
            os.system("clear")
            if len(filteredEntries) > 0:
                displayFilteredMenu(menuChoice, filteredEntries, totalNrOfMatches)
                displayPageFooter(syncedCurrentDir, menuChoice, appliedFilterKey)
                userInput = input()
                os.system("clear")
        elif len(userInput) == 0:
            os.system("clear")
            isMenuEmpty = self.nav.isHistoryMenuEmpty() if menuChoice == "-h" else self.nav.isFavoritesMenuEmpty()
            if not isMenuEmpty:
                displayHistMenu() if menuChoice == "-h" else displayFavoritesMenu()
                displayPageFooter(syncedCurrentDir, menuChoice)
                userInput = input()
                os.system("clear")
        # process user choice
        userInput = userInput.strip()
        choiceResult = self.nav.chooseFilteredMenuEntry(userInput, filteredEntries) if menuChoice in ["-fh", "-ff"] else self.nav.chooseHistoryMenuEntry(userInput) if menuChoice == "-h" else self.nav.chooseFavoritesMenuEntry(userInput)
        return choiceResult

    """ Function used for displaying specific navigation menus """
    def __displayFormattedNavFileContent__(self, fileContent, firstRowNr = 0, limit = -1):
        nrOfRows = len(fileContent)
        assert nrOfRows > 0, "Attempt to display an empty navigation menu"
        limit = nrOfRows if limit < 0 or limit > nrOfRows else limit
        assert limit != 0, "Zero entries limit detected, not permitted"
        beginCharsToDisplayForDirName = navset.max_nr_of_item_name_chars // 2 #first characters to be displayed for a directory name exceeding the maximum number of chars to be displayed
        endCharsToDisplayForDirName = beginCharsToDisplayForDirName - navset.max_nr_of_item_name_chars #last characters to be displayed for a directory name exceeding the maximum number of chars to be displayed
        beginCharsToDisplayForPath = navset.max_nr_of_path_chars // 2 #first characters to be displayed for an absolute path exceeding the maximum number of chars to be displayed
        endCharsToDisplayForPath = beginCharsToDisplayForPath - navset.max_nr_of_path_chars #last characters to be displayed for an absolute path exceeding the maximum number of chars to be displayed
        if firstRowNr < limit and firstRowNr >= 0:
            print('{0:<5s} {1:<40s} {2:<40s} {3:<85s}'.format('', '- PARENT DIR -', '- DIR NAME -', '- DIR PATH -'))
            for rowNr in range(firstRowNr, limit):
                dirPath = fileContent[rowNr].strip('\n')
                dirName = os.path.basename(dirPath) if dirPath != "/" else "*root"
                parentDir = os.path.basename(str(Path(dirPath).parent))
                if len(parentDir) == 0:
                    parentDir = "*root"
                elif len(parentDir)-1 > navset.max_nr_of_item_name_chars:
                    parentDir = parentDir[0:beginCharsToDisplayForDirName] + "..." + parentDir[endCharsToDisplayForDirName-1:]
                if len(dirName)-1 > navset.max_nr_of_item_name_chars:
                    dirName = dirName[0:beginCharsToDisplayForDirName] + "..." + dirName[endCharsToDisplayForDirName-1:]
                if len(dirPath)-1 > navset.max_nr_of_path_chars:
                    dirPath = dirPath[0:beginCharsToDisplayForPath] + "..." + dirPath[endCharsToDisplayForPath-1:]
                print('{0:<5s} {1:<40s} {2:<40s} {3:<85s}'.format(str(rowNr+1), parentDir, dirName, dirPath))
