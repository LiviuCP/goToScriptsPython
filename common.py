""" common code to be used by cmd_menus.update.py and nav_menus_update.py """

import os
from os.path import expanduser

home_dir = expanduser("~") + "/"
input_storage_file = home_dir + ".store_input"
output_storage_file = home_dir + ".store_output"

def limitEntriesNr(filePath, maxEntries):
    with open(filePath, "r") as f:
        fileContent = f.readlines()
        fileEntries = 0
        for entry in fileContent:
            fileEntries = fileEntries + 1
        if fileEntries > maxEntries:
            f.close()
            with open(filePath, "w") as f:
                for entryNr in range(0, maxEntries):
                    f.write(fileContent[entryNr])

"""
The returned outcome could have following special values in the first field:
:1 - user input to be forwarded as regular input (path name/command)
:2 - user exited the command menu, returned to navigation mode
:3 - invalid first argument
:4 - empty menu
"""
def getMenuEntry(userInput, content):
    def isInputValid(userInput, content):
        isValid = True
        if userInput.isdigit():
            intInput = int(userInput)
            if intInput > len(content) or intInput == 0:
                isValid = False
        else:
            isValid = False
        return isValid
    if isInputValid(userInput, content):
        userInput = int(userInput) - 1
        output = content[userInput]
    else:
        output = ":4" if len(content) == 0 else ":2" if userInput == '!' else ":1"
    return (output.strip("\n"), userInput, "")

# if a valid absolute path is fed as argument the unchanged path (without any ending '/') is returned
def getAbsoluteDirPath(dirPath):
    if dirPath == "":
        pathToAdd = os.getcwd()
    else:
        pathToAdd = dirPath
        with open(input_storage_file, "w") as inputStorage:
            inputStorage.write(pathToAdd)
        # build BASH command for retrieving the absolute path of the replacing dir (if exists)
        command = "input=`head -1 " + input_storage_file + "`; "
        command = command + "output=" + output_storage_file + "; "
        command = command + "cd $input 2> /dev/null; if [[ $? == 0  ]]; then pwd > \"$output\"; else echo :4 > \"$output\"; fi"
        os.system(command)
        with open(output_storage_file, "r") as outputStorage:
            pathToAdd = outputStorage.readline().strip('\n')
        if pathToAdd == ":4":
            pathToAdd = ""
    return pathToAdd

def getNumberOfLines(filePath):
    nrLines = 0
    with open(filePath, "r") as fPath:
        for entry in fPath.readlines():
            nrLines = nrLines + 1
    return nrLines

def displayFormattedNavFileContent(fileContent, firstRowNr = 0, limit = -1):
    nrOfRows = len(fileContent)
    limit = nrOfRows if limit < 0 or limit > nrOfRows else limit
    if firstRowNr < limit and firstRowNr >= 0:
        for rowNr in range(firstRowNr, limit):
            dirPath = fileContent[rowNr].strip('\n')
            print('{0:<10s} {1:<30s} {2:<160s}'.format(str(rowNr+1), os.path.basename(dirPath), dirPath))

def displayFormattedCmdFileContent(fileContent, firstRowNr = 0, limit = -1):
    nrOfRows = len(fileContent)
    limit = nrOfRows if limit < 0 or limit > nrOfRows else limit
    if firstRowNr < limit and firstRowNr >= 0:
        for rowNr in range(firstRowNr, limit):
            command = fileContent[rowNr].strip('\n')
            print('{0:<10s} {1:<140s}'.format(str(rowNr+1), command))
