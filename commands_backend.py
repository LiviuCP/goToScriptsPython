import sys, os
import nav_cmd_common as nvcdcmn, commands_settings as cmdset, system_settings as sysset

class CommandsBackend:
    def __init__(self):
        self.recentCommandsHistory = []
        self.persistentCommandsHistory = {}
        self.dailyCommandsLog = []
        self.consolidatedCommandsHistory = []
        self.__loadCommandsFiles()
        self.__consolidateCommandsHistory()

    def chooseCommand(self, userInput):
        return nvcdcmn.getMenuEntry(userInput, self.consolidatedCommandsHistory)

    def chooseFilteredCommand(self, userInput, filteredContent):
        return nvcdcmn.getMenuEntry(userInput, filteredContent)

    def isCommandsMenuEmpty(self):
        return len(self.consolidatedCommandsHistory) == 0

    def updateCommandsHistory(self, command):
        assert len(command) > 0, "Empty command argument detected"
        # handle recent history
        if command in self.recentCommandsHistory:
            self.recentCommandsHistory.remove(command)
        elif len(self.recentCommandsHistory) == cmdset.c_r_hist_max_entries:
            self.recentCommandsHistory.pop(len(self.recentCommandsHistory)-1)
        self.recentCommandsHistory = [command] + self.recentCommandsHistory
        # handle persistent history
        if command not in self.dailyCommandsLog:
            self.dailyCommandsLog.append(command)
            if command in self.persistentCommandsHistory.keys():
                self.persistentCommandsHistory[command] += 1
            else:
                self.persistentCommandsHistory[command] = 1
        self.__consolidateCommandsHistory()

    def clearCommandsHistory(self):
        self.recentCommandsHistory.clear()
        self.persistentCommandsHistory.clear()
        self.consolidatedCommandsHistory.clear()
        self.dailyCommandsLog.clear()

    def buildFilteredCommandsHistory(self, filterKey, filteredContent):
        assert len(filterKey) > 0, "Empty filter key found"
        return nvcdcmn.buildFilteredPersistentHistory(self.persistentCommandsHistory, filterKey, cmdset.max_filtered_c_hist_entries, filteredContent)

    def displayFormattedRecentCmdHistContent(self):
        self.__displayFormattedCmdFileContent(self.consolidatedCommandsHistory, 0, len(self.recentCommandsHistory))

    def displayFormattedPersistentCmdHistContent(self):
        self.__displayFormattedCmdFileContent(self.consolidatedCommandsHistory, len(self.recentCommandsHistory))

    def displayFormattedFilteredCmdHistContent(self, filteredContent, totalNrOfMatches):
        self.__displayFormattedCmdFileContent(filteredContent, 0)
        print("")
        print("\tThe search returned " + str(totalNrOfMatches) + " match(es).")
        if totalNrOfMatches > len(filteredContent):
            print("\tFor better visibility only part of them are displayed. Please narrow the search if needed.")

    def closeCommands(self):
        self.__saveCommandsFiles()
        pass

    def __loadCommandsFiles(self):
        nvcdcmn.loadBasicFiles(cmdset.c_r_hist_file, cmdset.c_r_hist_max_entries, cmdset.c_l_hist_file, cmdset.c_p_str_hist_file, cmdset.c_p_num_hist_file, self.recentCommandsHistory, self.dailyCommandsLog, self.persistentCommandsHistory)

    def __saveCommandsFiles(self):
        nvcdcmn.writeBackToTempHist(self.recentCommandsHistory, cmdset.c_r_hist_file, self.dailyCommandsLog, cmdset.c_log_dir, cmdset.c_l_hist_file)
        nvcdcmn.writeBackToPermHist(self.persistentCommandsHistory, cmdset.c_p_str_hist_file, cmdset.c_p_num_hist_file)

    def __displayFormattedCmdFileContent(self, fileContent, firstRowNr = 0, limit = -1):
        nrOfRows = len(fileContent)
        assert nrOfRows > 0, "Attempt to display an empty command menu"
        limit = nrOfRows if limit < 0 or limit > nrOfRows else limit
        assert limit != 0, "Zero entries limit detected, not permitted"
        if firstRowNr < limit and firstRowNr >= 0:
            for rowNr in range(firstRowNr, limit):
                command = fileContent[rowNr].strip('\n')
                print('{0:<10s} {1:<140s}'.format(str(rowNr+1), command))
    def __consolidateCommandsHistory(self):
        cpHistEntries = []
        limit = 0
        for command, executionsCount in sorted(self.persistentCommandsHistory.items(), key = lambda k:(k[1], k[0].lower()), reverse = True):
            if (limit == cmdset.c_p_hist_max_entries):
                break
            cpHistEntries.append(command)
            limit += 1
        cpHistEntries.sort(key = lambda k: k.lower())
        self.consolidatedCommandsHistory = self.recentCommandsHistory.copy()
        for command in cpHistEntries:
            self.consolidatedCommandsHistory.append(command)

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

def buildShellCommand(command):
    assert len(command) > 0, "Empty command argument detected"
    sourceConfigFileCmd = "source ~/.bashrc;" #include .bashrc to ensure the aliases and scripts work
    getExitCodeCmd = "echo $? > " + sysset.output_storage_file #exit code (used by Python to determine if the command finished successfully or not)
    shellCommandToExecute = sourceConfigFileCmd + "\n" + command + "\n" + getExitCodeCmd
    return shellCommandToExecute

def retrieveCommandExecResult():
    result = -1
    with open(sysset.output_storage_file, "r") as output:
        result = int(output.readline().strip('\n'))
    return result
