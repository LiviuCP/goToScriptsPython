import os, readline
import commands_backend as cmd, commands_settings as cmdset, system_functionality as sysfunc, common, display as out

class Commands:
    def __init__(self):
        self.previousCommand = ""
        self.previousCommandSuccess = False
        self.previousCommandsFilter = ""
        self.cmd = cmd.CommandsBackend()

    def getPreviousCommand(self):
        return self.previousCommand

    def getPreviousCommandSuccess(self):
        return self.previousCommandSuccess

    def getPreviousCommandsFilter(self):
        return self.previousCommandsFilter

    """ execute new command """
    def executeCommand(self, command):
        assert len(command) > 0, "Empty argument detected for 'command'"
        result = (0, "", "")
        if (cmd.isSensitiveCommand(command)):
            command = handleSensitiveCommand(command)
        if command is not None:
            print(f"Entered command is being executed: {command}")
            print("-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-")
            result = self.__executeCommand__(command)
            finishingStatus = "successfully" if self.previousCommandSuccess else "with errors"
            print("-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-")
            print(f"Entered command finished {finishingStatus}! Scroll up to check output (if any) if it exceeds the screen.")
        return result

    """ execute (repeat) previous command """
    def executePreviousCommand(self):
        result = None
        if len(self.previousCommand) > 0:
            command = self.previousCommand
            if (cmd.isSensitiveCommand(command)):
                command = handleSensitiveCommand(command)
            if command is not None:
                print(f"Repeated command is being executed: {command}")
                print("-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-")
                result = self.__executeCommand__(command)
                finishingStatus = "successfully" if self.previousCommandSuccess else "with errors"
                print("-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-")
                print(f"Repeated command finished {finishingStatus}! Scroll up to check output (if any) if it exceeds the screen.")
        else:
            print("No shell command previously executed")
        return result

    """ edit and execute previous command """
    def editAndExecutePreviousCommand(self):
        return self.__editAndExecuteCommand__(self.previousCommand)

    """ Displays the requested commands menu and prompts the user to enter the required option """
    def visitCommandsMenu(self, mode, filterKey = ""):
        def displayCmdHistMenu(mode):
            (consolidatedCommandsHistory, recentCommandsHistoryEntriesCount) = self.cmd.getHistoryInfo()
            print("COMMANDS LIST")
            print("")
            print("**** EXECUTE MODE ****") if mode == "--execute" else print("**** EDIT MODE ****")
            print("")
            print("-- RECENTLY EXECUTED --")
            print("")
            self.__displayFormattedCmdFileContent__(consolidatedCommandsHistory, 0, recentCommandsHistoryEntriesCount)
            print("")
            print("-- MOST EXECUTED --")
            print("")
            self.__displayFormattedCmdFileContent__(consolidatedCommandsHistory, recentCommandsHistoryEntriesCount)
        def displayFilteredCmdHistMenu(filteredContent, mode, totalNrOfMatches):
            print("FILTERED COMMANDS LIST")
            print("")
            print("**** EXECUTE MODE ****") if mode == "--execute" else print("**** EDIT MODE ****")
            print("")
            self.__displayFormattedCmdFileContent__(filteredContent, 0)
            print("")
            print(f"\tThe search returned {str(totalNrOfMatches)} match(es).")
            if totalNrOfMatches > len(filteredContent):
                print("\tFor better visibility only part of them are displayed. Please narrow the search if needed.")
        def displayPageFooter(currentDir, filterKey = ""):
            print("")
            print(f"Current directory: {currentDir}")
            print("Last executed shell command: ", end='')
            print(self.previousCommand) if len(self.previousCommand) > 0 else print("none")
            print("")
            if len(filterKey) > 0:
                print(f"Applied filter: {filterKey}")
                print("")
            print("Enter command number.")
            print("Enter :t to toggle to ", end='')
            print("EDIT MODE.") if mode == "--execute" else print("EXECUTE MODE.")
            print("")
            print("Enter ! to quit.")
            print("")
        syncedCurrentDir, fallbackPerformed = sysfunc.syncCurrentDir()
        assert not fallbackPerformed, "Current dir fallback not allowed"
        status = 0 # default status (normal execution)
        passedInput = ""
        assert mode in ["--edit", "--execute"], "Invalid mode argument provided"
        os.system("clear")
        filteredEntries = []
        isValidQuickHistEntryNr = self.cmd.isValidQuickHistoryEntryNr(filterKey);
        if self.cmd.isHistoryMenuEmpty():
            print("There are no entries in the command history menu.")
            userInput = ""
        elif len(filterKey) == 0:
            displayCmdHistMenu(mode)
            displayPageFooter(syncedCurrentDir)
            userInput = input()
            os.system("clear")
        elif isValidQuickHistEntryNr:
            userInput = filterKey;
        else:
            self.previousCommandsFilter = filterKey
            totalNrOfMatches, appliedFilterKey = self.cmd.buildFilteredHistory(filterKey, filteredEntries)
            if len(filteredEntries) == 0:
                print("There are no entries in the filtered command history menu.")
                userInput = ""
            else:
                displayFilteredCmdHistMenu(filteredEntries, mode, totalNrOfMatches)
                displayPageFooter(syncedCurrentDir, appliedFilterKey)
                userInput = input()
                os.system("clear")
        # process user choice
        userInput = userInput.strip()
        commandsHistoryEntry, chooseCommandPassedInput, chooseCommandPassedOutput = self.cmd.chooseHistoryMenuEntry(userInput) if (len(filterKey) == 0 or isValidQuickHistEntryNr) else self.cmd.chooseFilteredMenuEntry(userInput, filteredEntries)
        syncedCurrentDir, fallbackPerformed = sysfunc.syncCurrentDir() # handle the case when current dir becomes unreachable in the time interval between entering commands menu and entering choice
        if fallbackPerformed:
            out.displayFallbackMessage()
        elif commandsHistoryEntry in [":1", ":2"]:
            status = int(commandsHistoryEntry[1])
            passedInput = chooseCommandPassedInput
            if status == 2:
                print("You exited the command menu!")
        elif commandsHistoryEntry not in [":3", ":4"]:
            commandExecStatus = status
            passedCommandExecInput = ""
            passedCommandExecOutput = ""
            if mode == "--execute":
                commandToExecute = commandsHistoryEntry
                if cmd.isSensitiveCommand(commandToExecute):
                    commandToExecute = handleSensitiveCommand(commandToExecute)
                if commandToExecute is not None:
                    print(f"Repeated command is being executed: {commandToExecute}")
                    print("-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-")
                    commandExecStatus, passedCommandExecInput, passedCommandExecOutput = self.__executeCommand__(commandToExecute)
                    finishingStatus = "successfully" if self.previousCommandSuccess else "with errors"
                    print("-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-")
                    print(f"Repeated command finished {finishingStatus}! Scroll up to check output (if any) if it exceeds the screen.")
                else:
                    commandExecStatus = 2
                    status = commandExecStatus
            else:
                commandExecStatus, passedCommandExecInput, passedCommandExecOutput = self.__editAndExecuteCommand__(commandsHistoryEntry)
                if commandExecStatus != 0:
                    status = 2 #aborted by user
            passedInput = passedCommandExecInput
        return (status, passedInput, "")

    """ resets the commands history """
    def clearCommandsHistory(self):
        self.cmd.clearHistory()
        print("Content of commands history menu has been erased.")

    """ quick commands history is part of recent history but can be accessed outside the regular history menus """
    def displayQuickCommandsHistory(self):
        (consolidatedHistory, recentHistoryEntriesCount) = self.cmd.getHistoryInfo()
        recentHistory = consolidatedHistory[0: recentHistoryEntriesCount]
        self.__displayFormattedCmdFileContent__(recentHistory, 0, cmdset.q_hist_max_entries)

    """ checks the entry number is a positive integer belonging to the range of entries contained in quick history (subset of recent commands history) """
    def isValidQuickCmdHistoryEntryNr(self, userInput):
        return self.cmd.isValidQuickHistoryEntryNr(userInput)

    """ requests closing the commands functionality in an orderly manner when application gets closed """
    def closeCommands(self):
        return self.cmd.close()

    """ edit an existing command (previous command or from commands history) and then execute it """
    def __editAndExecuteCommand__(self, previousCommand):
        def hook():
            readline.insert_text(previousCommand)
            readline.redisplay()
        status = 0 #normal execution, no user abort
        passedInput = ""
        if len(previousCommand) == 0:
            print("No shell command executed in this session. Enter a new command")
        else:
            print("Please edit the below command and hit ENTER to execute")
            readline.set_pre_input_hook(hook)
        print("(press \':\' + ENTER to quit):")
        commandToExecute = input()
        commandToExecute = commandToExecute.rstrip(' ') #there should be no trailing spaces, otherwise the entries might get duplicated in the command history
        readline.set_pre_input_hook() # ensure any further input is no longer pre-filled
        os.system("clear")
        commandLength = len(commandToExecute)
        syncedCurrentDir, fallbackPerformed = sysfunc.syncCurrentDir() #in case current dir gets unreachable before user enters input ...
        if fallbackPerformed:
            out.displayFallbackMessage()
        elif commandLength > 0 and commandToExecute[commandLength-1] != ':':
            if (cmd.isSensitiveCommand(commandToExecute)):
                commandToExecute = handleSensitiveCommand(commandToExecute)
            if commandToExecute is not None:
                commandType = "Edited" if previousCommand != "" else "Entered"
                print(f"{commandType} command is being executed: {commandToExecute}")
                print("-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-")
                commandExecStatus, passedCommandExecInput, passedCommandExecOutput = self.__executeCommand__(commandToExecute)
                finishingStatus = "successfully" if self.previousCommandSuccess else "with errors"
                print("-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-")
                print(f"{commandType} command finished {finishingStatus}! Scroll up to check output (if any) if it exceeds the screen.")
                passedInput = passedCommandExecInput
            else:
                status = 2 # sensitive command aborted by user
        else:
            print("Command aborted. You returned to navigation menu.")
            status = 2 #aborted by user
        return (status, passedInput, "")

    """ core command execution function """
    def __executeCommand__(self, command):
        assert len(command) > 0, "Empty command has been provided"
        commandExecResult = os.system(command)
        if len(command) >= cmd.getMinCommandSize():
            self.cmd.updateHistory(command)
        self.previousCommand = command
        self.previousCommandSuccess = (commandExecResult == 0)
        return (0, command, "")

    """ Function used for displaying specific commands menus """
    def __displayFormattedCmdFileContent__(self, fileContent, firstRowNr = 0, limit = -1):
        nrOfRows = len(fileContent)
        assert nrOfRows > 0, "Attempt to display an empty command menu"
        limit = nrOfRows if limit < 0 or limit > nrOfRows else limit
        assert limit != 0, "Zero entries limit detected, not permitted"
        if firstRowNr < limit and firstRowNr >= 0:
            for rowNr in range(firstRowNr, limit):
                command = fileContent[rowNr].strip('\n')
                print('{0:<10s} {1:<140s}'.format(str(rowNr+1), command))

def handleSensitiveCommand(command):
    syncedCurrentDir, fallbackPerformed = sysfunc.syncCurrentDir()
    assert not fallbackPerformed, "Current dir fallback not allowed"
    print("The following command might cause ireversible changes:")
    print(command)
    print("")
    print("Current directory: ")
    print(syncedCurrentDir)
    print("")
    print("Are you sure you want to continue?")
    print("")
    choice = common.getInputWithTextCondition("Enter your choice (y/n): ", lambda userInput: userInput.lower() not in {'y', 'n'}, \
                                          "Invalid choice selected. Please try again")
    os.system("clear")
    if choice.lower() == "n":
        command = None
        print("Command aborted. You returned to navigation menu.")
    return command
