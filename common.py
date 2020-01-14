""" common code to be used by cmd_menus.update.py and nav_menus_update.py """

import os, sys, readline
from os.path import expanduser
from pathlib import Path

home_dir = expanduser("~") + "/"
input_storage_file = home_dir + ".store_input"
output_storage_file = home_dir + ".store_output"

max_nr_of_dir_name_chars = 25
max_nr_of_path_chars = 75

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
            inputStorage.close() # file needs to be closed otherwise the below executed BASH command might return unexpected results
            # build BASH command for retrieving the absolute path of the replacing dir (if exists)
            command = "input=`head -1 " + input_storage_file + "`; "
            command = command + "output=" + output_storage_file + "; "
            command = command + "cd $input 2> /dev/null; if [[ $? == 0  ]]; then pwd > \"$output\"; else echo :4 > \"$output\"; fi"
            os.system(command)
            with open(output_storage_file, "r") as outputStorage:
                pathToAdd = outputStorage.readline().strip('\n')
                pathToAdd = "" if pathToAdd == ":4" else pathToAdd
    return pathToAdd

def getNumberOfLines(filePath):
    with open(filePath, "r") as fPath:
        return len(fPath.readlines())

def displayFormattedNavFileContent(fileContent, firstRowNr = 0, limit = -1):
    beginCharsToDisplayForDirName = max_nr_of_dir_name_chars // 2 #first characters to be displayed for a directory name exceeding the maximum number of chars to be displayed
    endCharsToDisplayForDirName = beginCharsToDisplayForDirName - max_nr_of_dir_name_chars #last characters to be displayed for a directory name exceeding the maximum number of chars to be displayed
    beginCharsToDisplayForPath = max_nr_of_path_chars // 2 #first characters to be displayed for an absolute path exceeding the maximum number of chars to be displayed
    endCharsToDisplayForPath = beginCharsToDisplayForPath - max_nr_of_path_chars #last characters to be displayed for an absolute path exceeding the maximum number of chars to be displayed
    nrOfRows = len(fileContent)
    limit = nrOfRows if limit < 0 or limit > nrOfRows else limit
    if firstRowNr < limit and firstRowNr >= 0:
        print('{0:<5s} {1:<40s} {2:<40s} {3:<85s}'.format('', '- PARENT DIR -', '- DIR NAME -', '- DIR PATH -'))
        for rowNr in range(firstRowNr, limit):
            dirPath = fileContent[rowNr].strip('\n')
            dirName = os.path.basename(dirPath) if dirPath != "/" else "*root"
            parentDir = os.path.basename(str(Path(dirPath).parent))
            if parentDir == "":
                parentDir = "*root"
            elif len(parentDir)-1 > max_nr_of_dir_name_chars:
                parentDir = parentDir[0:beginCharsToDisplayForDirName] + "..." + parentDir[endCharsToDisplayForDirName-1:]
            if len(dirName)-1 > max_nr_of_dir_name_chars:
                dirName = dirName[0:beginCharsToDisplayForDirName] + "..." + dirName[endCharsToDisplayForDirName-1:]
            if len(dirPath)-1 > max_nr_of_path_chars:
                dirPath = dirPath[0:beginCharsToDisplayForPath] + "..." + dirPath[endCharsToDisplayForPath-1:]
            print('{0:<5s} {1:<40s} {2:<40s} {3:<85s}'.format(str(rowNr+1), parentDir, dirName, dirPath))

def displayFormattedCmdFileContent(fileContent, firstRowNr = 0, limit = -1):
    nrOfRows = len(fileContent)
    limit = nrOfRows if limit < 0 or limit > nrOfRows else limit
    if firstRowNr < limit and firstRowNr >= 0:
        for rowNr in range(firstRowNr, limit):
            command = fileContent[rowNr].strip('\n')
            print('{0:<10s} {1:<140s}'.format(str(rowNr+1), command))

def setPathAutoComplete():
    def getDirectoryContent(dirPath):
        if dirPath.startswith(os.path.sep): # case 1: absolute path
            dirName = os.path.dirname(dirPath)
            dirContent = os.listdir(dirName)
            dirContent = [os.path.join(dirName, name) for name in dirContent]
        else: # case 2: relative path, current directory
            dirContent = os.listdir(os.curdir)
        return dirContent
    def pathCompleter(inputText, state):
        results = [path for path in getDirectoryContent(inputText) if path.startswith(inputText)]
        return results[state]
    readline.set_completer(pathCompleter)
    readline.parse_and_bind("tab: complete")
    readline.set_completer_delims('`~!@#=+[{]}$%^&*()\\|;:\'",<>? \n\t')
