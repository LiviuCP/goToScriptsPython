import os, time, json, nav_cmd_common as nvcdcmn, commands_settings as cmdset

class CommandsBackend(nvcdcmn.NavCmdCommon):
    def __init__(self):
        super().__init__(cmdset)
        self.aliases = {}
        self.aliasesToAdd = {}
        self.aliasesToModify = {}
        self.aliasesToRemove = set({})
        self.aliasesLoadingTime = self.openingTime
        self.__loadFiles__()
        self.__consolidateHistory__()

    def expandCommand(self, command):
        resultingCommand = ""
        commandParts = command.split()
        aliasCandidate = commandParts[0]
        for alias, aliasReplacement in self.aliases.items():
            if aliasCandidate == alias:
                resultingCommand = aliasReplacement
                break
        if len(resultingCommand) > 0:
            commandParts.pop(0)
            for part in commandParts:
                resultingCommand += ' ' + part
        else:
            resultingCommand = command
        return resultingCommand

    def addOrModifyAlias(self, alias, aliasContent):
        assert isValidAlias(alias), "A valid alias is required!"
        assert len(aliasContent) > 0, "The alias content should not be empty!"
        addedOrModified = True
        if alias in self.aliases:
            if self.aliases[alias] != aliasContent:
                self.aliasesToModify[alias] = aliasContent
            else:
                # any previous modifications to be cancelled if alias entered with existing content
                if alias in self.aliasesToModify:
                    del self.aliasesToModify[alias]
                addedOrModified = False
            # any previous removal request to be cancelled no matter if content gets modified or not
            if alias in self.aliasesToRemove:
                self.aliasesToRemove.remove(alias)
        else:
            self.aliasesToAdd[alias] = aliasContent
        return addedOrModified

    def removeAlias(self, alias):
        assert isValidAlias(alias) > 0, "A valid alias is required!"
        removed = False
        if alias in self.aliases:
            self.aliasesToRemove.add(alias)
            if alias in self.aliasesToModify:
                del self.aliasesToModify[alias]
            removed = True
        elif alias in self.aliasesToAdd:
            del self.aliasesToAdd[alias]
        return removed

    def handleUpdatingAliasesFinished(self, shouldSaveChanges):
        if shouldSaveChanges:
            for alias in self.aliasesToRemove:
                del self.aliases[alias]
            for alias, aliasContent in self.aliasesToModify.items():
                self.aliases[alias] = aliasContent
            for alias, aliasContent in self.aliasesToAdd.items():
                self.aliases[alias] = aliasContent
            self.__saveAliasesFile__()
        self.__clearAliasChanges__()

    def refreshAliases(self):
        if os.path.isfile(cmdset.aliases_file) and os.path.getmtime(cmdset.aliases_file) > self.aliasesLoadingTime:
            self.__loadAliasesFile__()

    def getPendingAliasesUpdates(self):
        return (self.aliasesToAdd, self.aliasesToModify, self.aliasesToRemove)

    def areAliasesUpdatesPending(self):
        return len(self.aliasesToAdd) > 0 or len(self.aliasesToModify) > 0 or len(self.aliasesToRemove) > 0

    def getAliases(self):
        return self.aliases.items()

    def __loadFiles__(self):
         super().__loadFiles__()
         self.__loadAliasesFile__()

    def __loadAliasesFile__(self):
        aliasesJsonContent = ""
        if os.path.isfile(self.settings.aliases_file):
            with open(self.settings.aliases_file, "r") as alias:
                aliasesJsonContent = alias.readline()
                self.aliasesLoadingTime = time.time()
        if len(aliasesJsonContent) > 0:
            try:
                self.aliases = json.loads(aliasesJsonContent)
                aliasesToRemove = []
                for alias, aliasContent in self.aliases.items():
                    if not isValidAlias(alias) or len(aliasContent) == 0:
                        aliasesToRemove.append(alias)
                for alias in aliasesToRemove:
                    del self.aliases[alias]
            except json.JSONDecodeError:
                print(f"Invalid JSON file format in file: {self.settings.aliases_file}")

    def __saveAliasesFile__(self):
        aliasesJsonContent = json.dumps(self.aliases) if len(self.aliases) > 0 else "{}"
        with open(self.settings.aliases_file, "w") as alias:
            alias.write(aliasesJsonContent)

    def __clearAliasChanges__(self):
        self.aliasesToAdd.clear()
        self.aliasesToModify.clear()
        self.aliasesToRemove.clear()

    def __reconcileFiles__(self):
        currentRecentHistory = self.recentHistory.copy()
        currentPersistentHistory = self.persistentHistory.copy()
        currentDailyCommandsLog = self.dailyLog.copy()
        self.__loadFiles__() # reload history files of previous session
        self.recentHistory = currentRecentHistory # restore current recent history
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

def isValidAlias(alias):
    return len(alias) > 0 and alias.isalpha()
