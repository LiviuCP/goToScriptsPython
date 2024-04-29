""" common code to be used by navigation_backend.py and commands_backend.py """

import os, re, time
from pathlib import Path

class NavCmdCommon:
    def __init__(self, settings):
        self.recentHistory = []
        self.persistentHistory = {}
        self.dailyLog = []
        self.consolidatedHistory = []
        self.openingTime = time.time()
        self.settings = settings

    def chooseHistoryMenuEntry(self, userInput):
        return getMenuEntry(userInput, self.consolidatedHistory)

    def chooseFilteredMenuEntry(self, userInput, filteredContent):
        return getMenuEntry(userInput, filteredContent)

    def updateHistory(self, entry):
        assert len(entry) > 0, "Empty argument detected"
        # handle recent history
        self.__updateRecentHistory__(entry)
        # handle permanent history
        addedToDailyLog = self.__addToDailyLog__(entry)
        if addedToDailyLog:
            self.__updatePermanentHistory__(entry)
        self.__consolidateHistory__()

    def clearHistory(self):
        self.recentHistory.clear()
        self.persistentHistory.clear()
        self.consolidatedHistory.clear()
        self.dailyLog.clear()

    def buildFilteredHistory(self, filterKey, filteredContent):
        assert len(filterKey) > 0, "Empty filter key found"
        rawHistoryContent = [path for path, count in sorted(self.persistentHistory.items(), key = lambda k:(k[1], k[0].lower()), reverse = True)]
        return buildFilteredHistory(rawHistoryContent, filterKey, self.settings.max_filtered_hist_entries, filteredContent)

    def getHistoryInfo(self):
        return (self.consolidatedHistory.copy(), len(self.recentHistory))

    def isHistoryMenuEmpty(self):
        return len(self.consolidatedHistory) == 0

    def close(self):
        filesReconciled = False
        if self.__relevantFilesModifiedAfterStartup__():
            self.__reconcileFiles__()
            filesReconciled = True
        self.__saveFiles__()
        return filesReconciled

    def __loadFiles__(self, shouldOverrideRecentHistory = True):
        recentHistory = []
        persistentHistory = {}
        if os.path.isfile(self.settings.r_hist_file):
            with open(self.settings.r_hist_file, "r") as rHist:
                entriesCount = 0
                for entry in rHist.readlines():
                    if entriesCount == self.settings.r_hist_max_entries:
                        break
                    recentHistory.append(entry.strip('\n'))
                    ++entriesCount
        if len(recentHistory) > 0 and os.path.isfile(self.settings.p_str_hist_file) and os.path.isfile(self.settings.p_num_hist_file):
            readFromPermHist(self.settings.p_str_hist_file, self.settings.p_num_hist_file, persistentHistory)
        if len(persistentHistory) > 0:
            if shouldOverrideRecentHistory:
                self.recentHistory.clear()
                for entry in recentHistory:
                    self.recentHistory.append(entry)
            self.persistentHistory.clear()
            for strEntry, numEntry in persistentHistory.items():
                self.persistentHistory[strEntry] = numEntry
            if os.path.isfile(self.settings.l_hist_file):
                self.dailyLog.clear()
                with open(self.settings.l_hist_file, "r") as lHist:
                    for entry in lHist.readlines():
                        self.dailyLog.append(entry.strip('\n'))

    def __saveFiles__(self):
        with open(self.settings.r_hist_file, "w") as rHist:
            for entry in self.recentHistory:
                rHist.write(entry + '\n')
        if not os.path.exists(self.settings.log_dir):
            os.makedirs(self.settings.log_dir)
        with open(self.settings.l_hist_file, "w") as lHist:
            for entry in self.dailyLog:
                lHist.write(entry + '\n')
        writeBackToPermHist(self.persistentHistory, self.settings.p_str_hist_file, self.settings.p_num_hist_file)

    def __reconcileFiles__(self):
        raise NotImplementedError()

    def __relevantFilesModifiedAfterStartup__(self):
        return os.path.isfile(self.settings.p_str_hist_file) and os.path.getmtime(self.settings.p_str_hist_file) > self.openingTime

    def __updateRecentHistory__(self, entry):
        if entry in self.recentHistory:
            self.recentHistory.remove(entry)
        elif len(self.recentHistory) == self.settings.r_hist_max_entries:
            self.recentHistory.pop(len(self.recentHistory)-1)
        self.recentHistory = [entry] + self.recentHistory

    def __updatePersistentHistory__(self, entry):
        if entry in self.persistentHistory.keys():
            self.persistentHistory[entry] += 1
        else:
            self.persistentHistory[entry] = 1

    def __updatePermanentHistory__(self, entry):
        self.__updatePersistentHistory__(entry)

    def __consolidateHistory__(self):
        raise NotImplementedError()

    def __doConsolidateHistory__(self, chosenPersistentHistoryEntries):
        if chosenPersistentHistoryEntries is not None:
            self.consolidatedHistory = self.recentHistory.copy()
            self.consolidatedHistory.extend(chosenPersistentHistoryEntries)

    def __addToDailyLog__(self, entry):
        entryNotInDailyLog = entry not in self.dailyLog
        if entryNotInDailyLog:
            self.dailyLog.append(entry)
        return entryNotInDailyLog

    def __removeFromDailyLog__(self, entry):
        entryInDailyLog = entry in self.dailyLog
        if entryInDailyLog:
            self.dailyLog.remove(entry)
        return entryInDailyLog
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

def readFromPermHist(strHistFile, numHistFile, histDict):
    with open(strHistFile, "r") as strHist, open(numHistFile, "r") as numHist:
        strHistList = strHist.readlines()
        numHistList = numHist.readlines()
        assert len(strHistList) == len(numHistList), "The number of entries contained in file " + strHistFile + " is different from the number contained in file" + numHistFile
        histDict.clear()
        for strEntry, numEntry in zip(strHistList, numHistList):
            histDict[strEntry.strip('\n')] = int(numEntry.strip('\n'))

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
        except Exception:
            result.clear()
            nrOfMatches = 0
            appliedFilterKeyword = ""
    return (nrOfMatches, appliedFilterKeyword)
