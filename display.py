import os
import navigation_settings as navset, commands_settings as cmdset

def displayGeneralOutputUpperSection(currentDir, prevDir):
    assert os.path.exists(currentDir), "Invalid current directory path!"
    previousDirectory = "none" if len(prevDir) == 0 else prevDir
    print("")
    print("***************************************************************************************************************************************************************************************")
    print("")
    print(f"Current directory: {currentDir}")
    print(f"Previous directory: {previousDirectory}")
    print("")
    print("---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
    print("")
    print("Directory content (hidden items are excluded):")
    print("")
    displayDirContent(currentDir)
    print("")

def displayGeneralOutputLowerSection(prevCommand, navigationFilter, commandsFilter, clipboardAction, clipboardKeyword, clipboardSourceDir, recursiveTargetDir, syncWithFinder):
    lastCommand = "none"
    if len(prevCommand) > 0:
        lastCommand = prevCommand
    print("---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
    print("")
    print("Last executed command", end='')
    if lastCommand != "none" and len(lastCommand) < cmdset.min_command_size:
        print(" (short)", end='')
    print(f": [ {lastCommand} ]")
    print("Last used filters: (navigation: ", end='')
    print(f"{navigationFilter}", end='') if len(navigationFilter) > 0 else print("[ none ]", end='')
    print(" / commands: ", end='')
    print(f"[ {commandsFilter} ])") if len(commandsFilter) > 0 else print("[ none ])")
    print("Clipboard action: ", end='')
    if len(clipboardAction) > 0:
        assert len(clipboardKeyword) > 0, "Invalid clipboard keyword"
        assert len(clipboardSourceDir) > 0, "Invalid clipboard source dir"
        print(f"[ {clipboardAction} (keyword: {clipboardKeyword}) ]")
    else:
        print("[ none ]")
    print("Clipboard source directory: ", end='')
    print(f"[ {clipboardSourceDir} ]") if len(clipboardSourceDir) > 0 else print("[ none ]")
    print("Recursive transfer target directory: ", end='')
    print(f"[ {recursiveTargetDir} ]") if len(recursiveTargetDir) > 0 else print("[ none ]")
    print("Sync with Finder enabled: ", end='')
    print("[ yes ]") if syncWithFinder == True else print("[ no ]")
    print("")
    print("***************************************************************************************************************************************************************************************")
    print("")
    print("Enter the path of the directory you want to visit (press ENTER to return to the home dir, enter ? for help or ! to quit).")
    print("")

def displayDirContent(dirPath):
    beginCharsToDisplay = navset.max_nr_of_item_name_chars // 2 #first characters to be displayed for a filename exceeding navset.max_nr_of_item_name_chars
    endCharsToDisplay = beginCharsToDisplay - navset.max_nr_of_item_name_chars #last characters to be displayed for a filename exceeding navset.max_nr_of_item_name_chars
    dirContent = []
    printAllItems = True
    for dirItem in os.listdir(dirPath):
        if dirItem[0] != ".": #exclude hidden files/directories
            if os.path.isdir(dirItem):
                dirItem = dirItem + "/"
                if len(dirItem)-1 > navset.max_nr_of_item_name_chars:
                    dirItem = dirItem[0:beginCharsToDisplay] + "..." + dirItem[endCharsToDisplay-1:]
            elif len(dirItem) > navset.max_nr_of_item_name_chars:
                dirItem = dirItem[0:beginCharsToDisplay] + "..." + dirItem[endCharsToDisplay:]
            dirContent.append(dirItem)
    dirContent.sort(key=lambda v: v.upper())
    nrOfItems = len(dirContent)
    if nrOfItems > navset.max_nr_of_displayed_items:
        printAllItems = False
        dirContent = dirContent[:navset.max_nr_of_displayed_items]
    printDirContentToColumns(dirContent)
    if not printAllItems:
        print(f"Number of items contained in the directory ({str(nrOfItems)}) exceeds the displayed ones ({str(navset.max_nr_of_displayed_items)})! Type :ls -p | less to display all directory items.")
    else:
        print(f"Number of items contained in the directory: {str(nrOfItems)}")

# to be updated: number of columns should be dynamically determined depending on screen size and number of files/dirs contained in current dir
def printDirContentToColumns(content):
    nrColumns = 5
    # add padding items so elements are equally distributed among rows
    extraItems = len(content) % nrColumns
    if extraItems != 0:
        for paddingItem in range(nrColumns - extraItems):
            content.append(" ")
    # print to colums, Z-sorted, ascending
    for rowNr in range(len(content) // nrColumns):
        baseIndex = rowNr * nrColumns
        print('{0:<40s} {1:<40s} {2:<40s} {3:<40s} {4:<40s}'.format(content[baseIndex], content[baseIndex + 1], content[baseIndex + 2], content[baseIndex + 3], content[baseIndex + 4]))
    print("")

def displayGeneralHelp(currentDir, fallbackOccurred):
    print("Navigation functions")
    print("")
    print("To navigate to a desired directory please enter the (relative/absolute) path (for home directory just press ENTER).")
    print("For executing any shell command please enter : followed by the command string.")
    print("For example enter :ls -l to list the contents of the current directory in detail.")
    print("")
    print("To cancel the user input without erasing the characters enter : as last character and press ENTER.")
    print("This also applies when editing a previously entered command.")
    print("")
    print("Following special options are available:")
    print("")
    print(":-    -  repeat last executed shell command (if any)")
    print(":     -  enter a shell command based on previous command")
    print(":<    -  enter command history menu (add keyword to get filtered entries)")
    print("::    -  enter command history menu to edit a previous command (add keyword to get filtered entries)")
    print("<     -  enter history menu")
    print(">     -  enter favorites menu")
    print(":q    -  enable/disable quick navigation/commands history")
    print(":n/:N -  apply previous navigation filter (if any) to navigation history/favorites")
    print(":f/:F -  apply previous command filter (if any) to command history in execute/edit mode")
    print(",     -  go to the previously visited directory")
    print(";[d]  -  go to ancestor directory located at depth d (e.g. ;3 is equivalent to entering relative path ../../..)")
    print("+>    -  add current directory to favorites")
    print("->    -  remove a directory from favorites")
    print(":s    -  toggle Finder sync on/off (for Mac OS only)")
    print("")
    print("To clear the navigation history enter :clearnavigation and press ENTER.")
    print("To clear the commands history enter :clearcommands and press ENTER.")
    print("")
    print("Other special options can be found by entering the clipboard/recursive and renaming help menus:")
    print("")
    print("?clip -  display help for clipboard and recursive operations")
    print("?ren  -  display help for renaming all items from current directory that are not hidden")
    print("")
    print("For direct navigation to a quick history (after enabling it, see above) or favorites menu entry please enter < or > followed by the entry number.")
    print("For direct navigation to the parent dir of a quick history entry (once this is enabled, see above) please enter ,, followed by the entry number.")
    print("For executing a command from quick history (after enabling it, see above) please enter - followed by the entry number.")
    print("For editing a command from quick history (after enabling it, see above) please enter + followed by the entry number.")
    print("For filtering navigation history (excluding favorites) please enter << followed by a search keyword.")
    print("For filtering favorites please enter >> followed by a search keyword.")
    print("Multiple search filters are allowed for navigation history, favorites and command history filtering (only results matching all filters are being displayed).")
    print("Use comma to separate the filters. Regex is supported.")
    print("")
    printCurrentDir(currentDir, fallbackOccurred)
    print("")

def displayClipboardHelp(currentDir, fallbackOccurred):
    print("Clipboard functions")
    print("")
    print("To add items to clipboard for moving or copying to another directory entering a keyword is required.")
    print("The keyword can contain the exact item name or wildcards, similar to executing the mv or cp commands.")
    print("The destination directory where the move/copy action is being executed should be different from source directory.")
    print("")
    print("It is also possible to recursively move/copy items to a target directory.")
    print("This needs to be setup prior to initiating the recursive operation and should be different from source directory.")
    print("")
    print("Following options are available:")
    print("")
    print(":m    -  add files and/or directories to clipboard for moving to another directory")
    print(":c    -  add files and/or directories to clipboard for copying to another directory")
    print(":y    -  execute move/copy action from clipboard")
    print(":ec   -  erase the clipboard")
    print(":dc   -  display the clipboard")
    print(":M    -  move files and/or directories recursively to the setup target directory")
    print(":C    -  copy files and/or directories recursively to the setup target directory")
    print(":td   -  setup current directory for recursive move/copy")
    print(":etd  -  erase setup target directory")
    print(":dtd  -  display setup target directory (if any)")
    print("")
    print("Press ? to check general help instructions.")
    print("")
    printCurrentDir(currentDir, fallbackOccurred)
    print("")

def displayRenamingHelp(currentDir, fallbackOccurred):
    print("Renaming functions")
    print("")
    print("You have the option to rename all items from current directory in a consistent manner.")
    print("The items can be files and/or directories and should NOT be hidden.")
    print("")
    print("Following options are available:")
    print("")
    print(":ra   -  rename items by appending a string to each of them")
    print(":ran  -  rename items by appending a number that gets incremented for each new item")
    print(":rp   -  same as :ra but prepends the string instead")
    print(":rpn  -  same as :ran but prepends the number instead")
    print(":ri   -  inserts a substring starting with the specified position within the item name")
    print(":rin  -  inserts an incrementing number starting with the specified position")
    print(":rd   -  deletes a substring starting with the specified position of the item name")
    print(":rr   -  replaces a number of characters starting with the specified position with a substring")
    print(":rrn  -  replaces a number of characters starting with the specified position with an incrementing number")
    print("")
    print("Depending on chosen operation you will be prompted to enter specific parameters. To abort before all params are given press ENTER.")
    print("If all params are entered and ok you will be asked to confirm operation. When this happens press y to confirm and n to abort renaming.")
    print("")
    print("Press ? to check general help instructions.")
    print("")
    printCurrentDir(currentDir, fallbackOccurred)
    print("")

def displayHelpMenuFooter():
    print("Enter the path of the directory you want to visit (press ENTER to return to the home dir).")
    print("Enter ! to quit navigation mode.")
    print("")

def printCurrentDir(currentDir, fallbackOccurred, label = "Current"):
    fallbackLabel = "(fallback)" if fallbackOccurred else ""
    print(f"{label} directory {fallbackLabel}: {currentDir}")

def printFallbackMessage(header = "Unable to perform operation!"):
    print(header)
    print("Current directory no longer reachable (probably deleted). It has been replaced by fallback directory.")
    print("")
    print("Please retry by considering the new current directory.")
