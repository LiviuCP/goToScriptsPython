import nav_cmd_common as nvcdcmn, commands_settings as cmdset

class CommandsBackend(nvcdcmn.NavCmdCommon):
    def __init__(self):
        super().__init__(cmdset)
        self.__loadFiles__()
        self.__consolidateHistory__()

    def __reconcileFiles__(self):
        currentPersistentHistory = self.persistentHistory.copy()
        currentDailyCommandsLog = self.dailyLog.copy()
        self.__loadFiles__(shouldOverrideRecentHistory = False) # member variables will contain the persistent history and the daily log of previous session
        # consolidate current and saved persistent history, reconcile number of times a command was executed
        for command, executionsCount in currentPersistentHistory.items():
            if command in self.persistentHistory.keys():
                if executionsCount > self.persistentHistory[command]:
                    self.persistentHistory[command] = executionsCount
            else:
                self.persistentHistory[command] = executionsCount
        # consolidate daily logs
        for command in currentDailyCommandsLog:
            self.__addToDailyLog__(command)

    def __consolidateHistory__(self):
        cpHistEntries = []
        limit = 0
        for command, executionsCount in sorted(self.persistentHistory.items(), key = lambda k:(k[1], k[0].lower()), reverse = True):
            if (limit == cmdset.p_hist_max_entries):
                break
            cpHistEntries.append(command)
            limit += 1
        cpHistEntries.sort(key = lambda k: k.lower())
        self.__doConsolidateHistory__(cpHistEntries)

    # TODO: move to nav_cmd_common.py
    def isValidQuickCmdHistoryEntryNr(self, userInput):
        isValid = False
        if len(userInput) > 0 and userInput.isdigit():
            quickCmdEntryNr = int(userInput)
            isValid = quickCmdEntryNr > 0 and quickCmdEntryNr <= len(self.recentHistory) and quickCmdEntryNr <= cmdset.q_hist_max_entries
        return isValid

""" command execution helper functions """
def isSensitiveCommand(command):
    assert len(command) > 0, "Empty command argument detected"
    isSensitive = False
    for keyword in cmdset.sensitive_commands_keywords:
        if keyword in command:
            isSensitive = True
            break
    return isSensitive

def getMinCommandSize():
    return cmdset.min_command_size
