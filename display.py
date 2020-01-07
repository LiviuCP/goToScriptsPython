import sys, os

max_nr_of_items = 50 #maximum number of files/dirs listed from current directory in navigation mode
max_nr_of_chars = 25 #maximum number of characters to be displayed for each item from current directory in navigation mode
begin_chars_to_display = max_nr_of_chars // 2 #first characters to be displayed for a filename exceeding max_nr_of_chars
end_chars_to_display = begin_chars_to_display - max_nr_of_chars #last characters to be displayed for a filename exceeding max_nr_of_chars

def displayGeneralOutput(prevDir, command = "", result = ""):
    previousDirectory = "none" if prevDir == "" else prevDir
    commandResult = ""
    if command == "" and result == "":
        lastCommand = 'none'
    elif result == "" or command == "":
        lastCommand = 'Error in displaying last command and its result!'
    else:
        lastCommand = command
        commandResult = result
    print("")
    print("****************************************************************************************************")
    print("")
    print("Current directory: " + os.getcwd())
    print("Previous directory: " + previousDirectory)
    print("")
    print("----------------------------------------------------------------------------------------------------")
    print("")
    print("Directory content (hidden items are excluded):")
    print("")
    displayCurrentDirContent()
    print("")
    print("----------------------------------------------------------------------------------------------------")
    print("")
    print("Last executed shell command", end='')
    if commandResult != "":
        print(" (finished " + commandResult + "):")
    else:
        print(":")
    print(lastCommand)
    print("")
    print("****************************************************************************************************")
    print("")
    print("Enter the path of the directory you want to visit (press ENTER to return to the home dir).")
    print("Enter ? for the list of of available commands or ! to quit navigation mode.'")
    print("")

def displayCurrentDirContent():
    dirContent = []
    printAllItems = True
    for dirItem in os.listdir("."):
        if dirItem[0] != ".": #exclude hidden files/directories
            if os.path.isdir(dirItem):
                dirItem = dirItem + "/"
                if len(dirItem)-1 > max_nr_of_chars:
                    dirItem = dirItem[0:begin_chars_to_display] + "..." + dirItem[end_chars_to_display-1:]
            elif len(dirItem) > max_nr_of_chars:
                dirItem = dirItem[0:begin_chars_to_display] + "..." + dirItem[end_chars_to_display:]
            dirContent.append(dirItem)
    dirContent.sort(key=lambda v: v.upper())
    nrOfItems = len(dirContent)
    if nrOfItems > max_nr_of_items:
        printAllItems = False
        dirContent = dirContent[:max_nr_of_items]
    printDirContentToColumns(dirContent)
    if printAllItems == False:
        print("Number of items contained in the directory (" + str(nrOfItems) + ") exceeds the displayed ones (" + str(max_nr_of_items) + ")! Type :ls -p | less to display all directory items.")
    else:
        print("Number of items contained in the directory: " + str(nrOfItems))

# to be updated: number of columns should be dynamically determined depending on screen size and number of files/dirs contained in current dir
def printDirContentToColumns(content):
    nrColumns = 4
    # add padding items so elements are equally distributed among rows
    extraItems = len(content) % nrColumns
    if extraItems != 0:
        for paddingItem in range(nrColumns - extraItems):
            content.append(" ")
    # print to colums, Z-sorted, ascending
    for rowNr in range(len(content) // nrColumns):
        baseIndex = rowNr * nrColumns
        print('{0:<40s} {1:<40s} {2:<40s} {3:<40s}'.format(content[baseIndex], content[baseIndex + 1], content[baseIndex + 2], content[baseIndex + 3]))
    print("")

def displayHelp():
    os.system("clear")
    print("Navigation functions")
    print("")
    print("For executing any shell command please enter : followed by the command string.")
    print("For example enter :ls -l to list the contents of the current directory in detail.")
    print("")
    print("")
    print("Other useful navigation options:")
    print("")
    print(":-    -  repeat last executed shell command (if any)")
    print(":     -  enter a shell command based on previous command")
    print(":<    -  enter command history menu")
    print("::    -  enter command history menu to edit a previous command")
    print("::<>   -  clear command history")
    print("<     -  enter history menu")
    print(">     -  enter favorites menu")
    print(",     -  go to the previously visited directory")
    print("+>    -  add current directory to favorites")
    print("->    -  remove a directory from favorites")
    print(":<>   -  clear navigation history")
    print("")
    print("For direct navigation to a history or favorites menu entry please enter < or > followed by a number.")
    print("Please do not put any spaces between operator and number.")
    print("")
    print("Current directory: "+os.getcwd())
    print("")
    print("Enter the path of the directory you want to visit (press ENTER to return to the home dir).")
    print("Enter ! to quit navigation mode.")
    print("")
