""" common code to be used by navigation_backend.py and commands_backend.py """

import os
from pathlib import Path

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

def readFromPermHist(histDict, strHistFile, numHistFile):
    with open(strHistFile, "r") as strHist, open(numHistFile, "r") as numHist:
        strHistList = strHist.readlines()
        numHistList = numHist.readlines()
        assert len(strHistList) == len(numHistList), "The number of entries contained in file " + strHistFile + " is different from the number contained in file" + numHistFile
        for index in range(len(strHistList)):
            histDict[strHistList[index].strip('\n')] = int(numHistList[index].strip('\n'))

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
