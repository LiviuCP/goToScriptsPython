""" Functions usable in any of the application modules """

import os, readline, subprocess
import navigation_settings as navset
from os.path import expanduser

# if a valid absolute path is fed as argument the unchanged path (without any ending '/') is returned
def getAbsoluteDirPath(dirPath):
    directory = navset.home_dir if len(dirPath) == 0 else dirPath
    expandDirCommand = "echo " + directory #if wildcards are being used the full dir name should be expanded
    result = subprocess.Popen(expandDirCommand, shell=True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    out,err = result.communicate()
    out = out.decode("utf-8").strip('\n')
    absoluteDirPath = ""
    if (os.path.isdir(out)):
        absoluteDirPath = os.path.abspath(out)
    return absoluteDirPath

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
        dirContent = []
        if dirPath.startswith(os.path.sep):
            dirContent = os.listdir(dirName)
        elif dirPath in ["~", ".", ".."]:
            dirContent = [entry for entry in os.listdir(os.curdir) if entry.startswith(dirPath)]
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
        for index, entry in enumerate(dirContent):
            if (entry.startswith('~') and entry != "~/" and os.path.isdir(expanduser('~') + entry[1:])) or \
               (os.path.isdir(entry) and entry not in ["~/", "./", "../"]):
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
    for char in path:
        if char in invalidChars:
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
