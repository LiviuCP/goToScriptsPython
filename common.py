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
    assert len(filePath) > 0, "Empty path argument detected"
    with open(filePath, "r") as f:
        fileContent = f.readlines()
        fileEntries = 0
        for entry in fileContent:
            fileEntries = fileEntries + 1
        if fileEntries > maxEntries:
            f.close()
            with open(filePath, "w") as f:
                for entryNr in range(maxEntries):
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
    # access parent dir of menu entry
    elif len(userInput) > 1 and userInput[0] == "," and isInputValid(userInput[1:], content):
        output = str(Path(content[int(userInput[1:])-1].strip("\n")).parent)
        userInput = ":parent" # used for further differentiation between entry directory and parent in case the returned path is invalid
    # retrieved path to be used for setting target dir from menu
    elif len(userInput) > 1 and userInput[0] == "+" and isInputValid(userInput[1:], content):
        output = str(Path(content[int(userInput[1:])-1].strip("\n")))
        userInput = ":preceding+" # used for further differentiation between entry directory and parent for setting target dir
    # retrieved parent path to be used for setting target dir from menu
    elif len(userInput) > 1 and userInput[0] == "-" and isInputValid(userInput[1:], content):
        output = str(Path(content[int(userInput[1:])-1].strip("\n")).parent)
        userInput = ":preceding-" # used for further differentiation between entry directory and parent for setting target dir
    else:
        output = ":4" if len(content) == 0 else ":2" if userInput == '!' else ":1"
    return (output.strip("\n"), userInput, "")

# if a valid absolute path is fed as argument the unchanged path (without any ending '/') is returned
def getAbsoluteDirPath(dirPath):
    if len(dirPath) == 0:
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
    assert len(filePath) > 0, "Empty file path argument detected"
    nrOfLines = 0
    with open(filePath, "r") as fPath:
        nrOfLines = len(fPath.readlines())
    return nrOfLines

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
            if len(parentDir) == 0:
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
        dirName = os.path.dirname(dirPath)
        if dirPath.startswith(os.path.sep):
            dirContent = os.listdir(dirName)
        elif dirPath in ["~", ".", ".."]:
            dirContent = []
            for entry in os.listdir(os.curdir):
                if entry.startswith(dirPath):
                    dirContent.append(entry)
            dirContent.append(dirPath + os.path.sep)
        elif dirPath.startswith("~") and dirPath[1] == os.path.sep:
            dirContent = os.listdir(expanduser('~') + dirName[1:])
        elif (dirPath.startswith("..") and dirPath[2] == os.path.sep) or (dirPath.startswith(".") and dirPath[1] == os.path.sep):
            dirContent = os.listdir(dirName)
        else:
            dirContent = os.listdir(os.curdir) if len(dirName) == 0 else os.listdir(dirName)
        # general auto-completion if no corner cases occur
        if len(dirContent) > 1 or dirContent[0] != dirPath:
            dirContent = [os.path.join(dirName, name) for name in dirContent]
        # terminate path with slash for directory to enable further auto-completion
        for index in range(len(dirContent)):
            if (dirContent[index].startswith('~') and dirContent[index] != "~/" and os.path.isdir(expanduser('~') + dirContent[index][1:])) or \
               (os.path.isdir(dirContent[index]) and dirContent[index] not in ["~/", "./", "../"]):
                dirContent[index] += os.path.sep
        return dirContent
    def pathCompleter(inputText, state):
        results = [path for path in getDirectoryContent(inputText) if path.startswith(inputText)]
        return results[state]
    readline.set_completer(pathCompleter)
    readline.parse_and_bind("tab: complete")
    readline.set_completer_delims('`!@#=+[{]}$%^&*()\\|;:\'",<>? \n\t')

# request user input: for required numeric input a condition must be fulfilled (empty input allowance should be stipulated in errorCondition)
def getInputWithNumCondition(requestMessage, isNumValRequired, errorCondition, errorMessage):
    resultingInput = ""
    isValidInput = False
    while not isValidInput:
        userInput = input(requestMessage)
        if isNumValRequired and ((len(userInput) > 0 and not userInput.isdigit()) or errorCondition(userInput)):
            print(errorMessage)
            print("")
        elif len(userInput) == 0:
            break
        else:
            resultingInput = userInput
            isValidInput = True
    return resultingInput

# request user input: any text input allowed, however an error condition may restrict this to some specific values (empty input allowance should also be stipulated in errorCondition)
def getInputWithTextCondition(requestMessage, errorCondition, errorMessage):
    resultingInput = ""
    isValidInput = False
    while not isValidInput:
        userInput = input(requestMessage)
        if errorCondition(userInput):
            print(errorMessage)
            print("")
        elif len(userInput) == 0:
            break
        else:
            resultingInput = userInput
            isValidInput = True
    return resultingInput

def addPaddingZeroes(number, totalDigits):
    result = str(number)
    assert result.isdigit() and int(result) >= 0, "The number is not valid (should be a non-negative integer)"
    while len(result) < totalDigits:
        result = "0" + result
    return result

""" Some paths should be excluded from visiting if they contain special characters like backslash as this might cause undefined script behavior """
def hasPathInvalidCharacters(path):
    assert path is not None and len(path) > 0, "Invalid path argument detected"
    invalidChars = {'\\'} # further characters considered invalid to be added here
    hasInvalidCharacters = False
    for index in range(len(path)):
        if path[index] in invalidChars:
            hasInvalidCharacters = True
            break
    return hasInvalidCharacters

def writeBackToPermHist(histDict, strHistFile, numHistFile, shouldSort = False):
    with open(strHistFile, "w") as strHist, open(numHistFile, "w") as numHist:
        if shouldSort:
            for path, count in sorted(histDict.items(), key = lambda k:(k[1], k[0].lower()), reverse = True):
                strHist.write(path + '\n')
                numHist.write(str(count) + '\n')
        else:
            for path, count in histDict.items():
                strHist.write(path + '\n')
                numHist.write(str(count) + '\n')
