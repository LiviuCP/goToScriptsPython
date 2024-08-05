""" common code to be used by navigation_backend.py and commands_backend.py """

import os, re, datetime, time, json
from utilities import common

class NavCmdCommon:
    def __init__(self, settings):
        self.recentHistory = []
        self.persistentHistory = {}
        self.dailyLog = set({})
        self.consolidatedHistory = []
        self.openingTime = time.time()
        self.settings = settings
        self.persistentHistoryJSONKey = "persistent_history"
        self.recentHistoryJSONKey = "recent_history"
        self.dailyLogJSONKeyPrefix = "daily_log_"
        self.dailyLogJSONKey = self.__computeDailyLogJSONKey__()

    def chooseHistoryMenuEntry(self, userInput):
        return self.__retrieveMenuEntry__(userInput, self.consolidatedHistory)

    def chooseFilteredMenuEntry(self, userInput, filteredContent):
        return self.__retrieveMenuEntry__(userInput, filteredContent)

    def updateHistory(self, entry):
        assert len(entry) > 0, "Empty argument detected"
        # handle recent history
        self.__updateRecentHistory__(entry)
        # handle permanent history
        self.__checkAndHandleOutdatedDailyLog__()
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

    def isValidQuickHistoryEntryNr(self, userInput):
        isValid = False
        if len(userInput) > 0 and userInput.isdigit():
            quickNavEntryNr = int(userInput)
            isValid = quickNavEntryNr > 0 and quickNavEntryNr <= len(self.recentHistory) and quickNavEntryNr <= self.settings.q_hist_max_entries
        return isValid

    def close(self):
        self.__checkAndHandleOutdatedDailyLog__()
        filesReconciled = False
        if self.__relevantFilesModifiedAfterStartup__():
            self.__reconcileFiles__()
            filesReconciled = True
        self.__saveFiles__()
        return filesReconciled

    def __loadFiles__(self):
        self.recentHistory.clear()
        self.persistentHistory.clear()
        self.dailyLog.clear()
        recentHistory = []
        persistentHistory = {}
        unifiedHistory = {}
        if os.path.isfile(self.settings.hist_file):
            with open(self.settings.hist_file, "r") as hist:
                unifiedHistoryAsJSON = hist.readline()
                try:
                    unifiedHistory = json.loads(unifiedHistoryAsJSON)
                except json.JSONDecodeError:
                    print(f"Invalid JSON file format in file: {self.settings.hist_file}")
        if self.recentHistoryJSONKey in unifiedHistory.keys():
            entriesCount = 0
            for entry in unifiedHistory[self.recentHistoryJSONKey]:
                if entriesCount == self.settings.r_hist_max_entries:
                    break
                recentHistory.append(entry.strip('\n'))
                ++entriesCount
        if len(recentHistory) > 0 and self.persistentHistoryJSONKey in unifiedHistory.keys():
            persistentHistory = unifiedHistory[self.persistentHistoryJSONKey]
        if len(persistentHistory) > 0:
            self.recentHistory = recentHistory
            self.persistentHistory = persistentHistory
            if self.dailyLogJSONKey in unifiedHistory.keys():
                for entry in unifiedHistory[self.dailyLogJSONKey]:
                    self.dailyLog.add(entry)

    def __saveFiles__(self):
        with open(self.settings.hist_file, "w") as hist:
            dailyLogKey = self.__computeDailyLogJSONKey__()
            dailyLogList = []
            for entry in self.dailyLog:
                dailyLogList.append(entry)
            unifiedHistory = {self.recentHistoryJSONKey:self.recentHistory, self.persistentHistoryJSONKey:self.persistentHistory, dailyLogKey:dailyLogList}
            unifiedHistoryAsJSON = json.dumps(unifiedHistory)
            hist.write(unifiedHistoryAsJSON)

    def __reconcileFiles__(self):
        raise NotImplementedError()

    def __relevantFilesModifiedAfterStartup__(self):
        return os.path.isfile(self.settings.hist_file) and os.path.getmtime(self.settings.hist_file) > self.openingTime

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
            self.dailyLog.add(entry)
        return entryNotInDailyLog

    def __removeFromDailyLog__(self, entry):
        entryInDailyLog = entry in self.dailyLog
        if entryInDailyLog:
            self.dailyLog.remove(entry)
        return entryInDailyLog

    def __checkAndHandleOutdatedDailyLog__(self):
        dailyLogJSONKey = self.__computeDailyLogJSONKey__()
        if dailyLogJSONKey != self.dailyLogJSONKey:
            self.dailyLogJSONKey = dailyLogJSONKey
            self.dailyLog.clear()

    def __computeDailyLogJSONKey__(self):
        return self.dailyLogJSONKeyPrefix + datetime.datetime.now().strftime("%Y%m%d")

    """
    The returned outcome could have following special values in the first field:
    :1 - user input to be forwarded as regular input (path name/command)
    :2 - user exited the command menu, returned to navigation mode
    :3 - reserved for future use
    :4 - empty menu
    """
    def __retrieveMenuEntry__(self, userInput, content):
        if common.isValidMenuEntryNr(userInput, content):
            userInput = int(userInput) - 1
            output = content[userInput].strip("\n")
        else:
            output = ":4" if len(content) == 0 else ":2" if userInput == '!' else ":1"
        return (output, userInput, "")

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
