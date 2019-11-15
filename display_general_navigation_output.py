import sys, os

maxNrOfItems = 50 #maximum number of files/dirs listed from current directory in navigation mode
maxNrOfChars = 25 #maximum number of characters to be displayed for each item from current directory in navigation mode
beginCharsToDisplay = maxNrOfChars // 2 #first characters to be displayed for a filename exceeding maxNrOfChars
endCharsToDisplay = beginCharsToDisplay - maxNrOfChars #last characters to be displayed for a filename exceeding maxNrOfChars

def displayNavOutput(command = "", result = ""):
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
    print("Current directory")
    print(os.getcwd())
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
                if len(dirItem)-1 > maxNrOfChars:
                    dirItem = dirItem[0:beginCharsToDisplay] + "..." + dirItem[endCharsToDisplay-1:]
            elif len(dirItem) > maxNrOfChars:
                dirItem = dirItem[0:beginCharsToDisplay] + "..." + dirItem[endCharsToDisplay:]
            dirContent.append(dirItem)

    dirContent.sort(key=lambda v: v.upper())

    nrOfItems = len(dirContent)
    if nrOfItems > maxNrOfItems:
        printAllItems = False
        dirContent = dirContent[:maxNrOfItems]

    printDirContentToColumns(dirContent)

    if printAllItems == False:
        print("Number of items contained in the directory (" + str(nrOfItems) + ") exceeds the displayed ones (" + str(maxNrOfItems) + ")! Type :ls -p | less to display all directory items.")
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
