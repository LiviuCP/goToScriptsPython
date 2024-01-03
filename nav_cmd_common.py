""" common code to be used by navigation_backend.py and commands_backend.py """

import os, re
from pathlib import Path

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

def loadBasicFiles(rHistFile, rHistMaxEntries, lHistFile, pStrHistFile, pNumHistFile, rHistEntries, dailyLog, pHistDict):
    recentHistory = []
    persistentHistory = {}
    if os.path.isfile(rHistFile):
        with open(rHistFile, "r") as rHist:
            entriesCount = 0
            for entry in rHist.readlines():
                if entriesCount == rHistMaxEntries:
                    break
                recentHistory.append(entry.strip('\n'))
                ++entriesCount
    if len(recentHistory) > 0 and os.path.isfile(pStrHistFile) and os.path.isfile(pNumHistFile):
        readFromPermHist(pStrHistFile, pNumHistFile, persistentHistory)
    if len(persistentHistory) > 0:
        rHistEntries.clear()
        pHistDict.clear()
        for entry in recentHistory:
            rHistEntries.append(entry)
        for entry in persistentHistory.items():
            pHistDict[entry[0]] = entry[1]
        if os.path.isfile(lHistFile):
            dailyLog.clear()
            with open(lHistFile, "r") as lHist:
                for entry in lHist.readlines():
                    dailyLog.append(entry.strip('\n'))

def readFromPermHist(strHistFile, numHistFile, histDict):
    with open(strHistFile, "r") as strHist, open(numHistFile, "r") as numHist:
        strHistList = strHist.readlines()
        numHistList = numHist.readlines()
        assert len(strHistList) == len(numHistList), "The number of entries contained in file " + strHistFile + " is different from the number contained in file" + numHistFile
        histDict.clear()
        for strEntry, numEntry in zip(strHistList, numHistList):
            histDict[strEntry.strip('\n')] = int(numEntry.strip('\n'))

def writeBackToTempHist(rHistEntries, rHistFile, dailyLog, logDir, dailyLogFile):
    with open(rHistFile, "w") as rHist:
        for entry in rHistEntries:
            rHist.write(entry + '\n')
    if not os.path.exists(logDir):
        os.makedirs(logDir)
    with open(dailyLogFile, "w") as lHist:
        for entry in dailyLog:
            lHist.write(entry + '\n')

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

def buildFilteredPersistentHistory(pHistDict, filterKeyword, maxFilteredHistEntries, filteredContent):
    assert len(filterKeyword) > 0, "Empty filter key found"
    rawHistoryContent = []
    for path, count in sorted(pHistDict.items(), key = lambda k:(k[1], k[0].lower()), reverse = True):
        rawHistoryContent.append(path)
    return buildFilteredHistory(rawHistoryContent, filterKeyword, maxFilteredHistEntries, filteredContent)

def buildFilteredHistory(rawContent, filterKeyword, maxFilteredHistEntries, filteredContent):
    assert len(filterKeyword) > 0, "Empty filter keyword found"
    nrOfMatches = 0
    appliedFilterKeyword = ""
    filters = filterKeyword.split(",")
    validFilters = []
    for filter in filters:
        filter = filter.lstrip()
        filter = filter.rstrip()
        #only valid (non-empty) filters are taken into consideration
        currentFilterLength = len(filter)
        if currentFilterLength > 0:
            if currentFilterLength > 1 and "-" == filter[0]:
                filter = "^((?!" + filter[1:] + ").)*$" # search for entries that DON'T contain the search keyword
            validFilters.append(filter.lower())
    if len(validFilters) > 0:
        result = []
        try:
            for entry in rawContent:
                entry = entry.strip('\n')
                match = True
                for filter in validFilters:
                    searchResult = re.search(filter, entry.lower())
                    if not searchResult:
                        match = False
                        break
                if match:
                    result.append(entry)
            nrOfMatches = len(result)
            nrOfExposedEntries = nrOfMatches if nrOfMatches < maxFilteredHistEntries else maxFilteredHistEntries
            for index in range(nrOfExposedEntries):
                filteredContent.append(result[index])
            # provide the cleaned-up filter string to the user
            for filter in validFilters:
                appliedFilterKeyword += filter + ", "
            appliedFilterKeywordLength = len(appliedFilterKeyword)
            if appliedFilterKeywordLength >= 2:
                appliedFilterKeyword = appliedFilterKeyword[0:appliedFilterKeywordLength-2]
        except Exception as e:
            result.clear()
            nrOfMatches = 0
            appliedFilterKeyword = ""
    return (nrOfMatches, appliedFilterKeyword)
