""" Functions usable in any of the application modules """

import os, sys, readline
import system_functionality as sysfunc, system_settings as sysset
from os.path import expanduser

# if a valid absolute path is fed as argument the unchanged path (without any ending '/') is returned
def getAbsoluteDirPath(dirPath):
    syncResult = sysfunc.syncCurrentDir()
    assert not syncResult[1], "Current directory fallback not allowed"
    if len(dirPath) == 0:
        pathToAdd = syncResult[0]
    else:
        pathToAdd = dirPath
        with open(sysset.input_storage_file, "w") as inputStorage:
            inputStorage.write(pathToAdd)
            inputStorage.close() # file needs to be closed otherwise the below executed BASH command might return unexpected results
            # build BASH command for retrieving the absolute path of the replacing dir (if exists)
            command = "input=`head -1 " + sysset.input_storage_file + "`; "
            command = command + "output=" + sysset.output_storage_file + "; "
            command = command + "cd $input 2> /dev/null; if [[ $? == 0  ]]; then pwd > \"$output\"; else echo :4 > \"$output\"; fi"
            os.system(command)
            with open(sysset.output_storage_file, "r") as outputStorage:
                pathToAdd = outputStorage.readline().strip('\n')
                pathToAdd = "" if pathToAdd == ":4" else pathToAdd
    return pathToAdd

def getNumberOfLines(filePath):
    assert len(filePath) > 0, "Empty file path argument detected"
    nrOfLines = 0
    with open(filePath, "r") as fPath:
        nrOfLines = len(fPath.readlines())
    return nrOfLines

# the menu content should be a list, user input should be a entry number starting from 1 and ending with the list length
def getMenuEntry(menuContent, userInput):
    assert type(menuContent) is list, "Invalid menu content data type!"
    result = None
    if userInput.isdigit():
        entryNumber = int(userInput)
        if entryNumber > 0 and entryNumber <= len(menuContent):
            result = menuContent[entryNumber-1]
    return result

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

""" Computes the relative path of an ancestor directory based on depth of its location (e.g. depth 2 would be ../.. meaning 2 steps below) """
def computeAncestorDirRelativePath(depth):
    path = ""
    if len(depth) > 0 and depth.isdecimal():
        stepsCount = int(depth)
        while stepsCount > 0:
            path = path + "../"
            stepsCount = stepsCount - 1
    return path
