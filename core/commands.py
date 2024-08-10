import os, readline
from system import system_functionality as sysfunc
from settings import commands_settings as cmdset
from utilities import common, display as out
from .private import commands_backend as cmd

class Commands:
    def __init__(self):
        self.rawCommand = "" # command as entered by user (might contain unexpanded aliases)
        self.previousCommand = ""
        self.previousCommandsFilter = ""
        self.cmd = cmd.CommandsBackend()

    def getPreviousCommand(self):
        return self.previousCommand

    def getPreviousCommandsFilter(self):
        return self.previousCommandsFilter

    """ execute new command """
    def executeCommand(self, command):
        assert len(command) > 0, "Empty argument detected for 'command'"
        command = self.__expandCommand__(command)
        result = (0, "", "")
        if (cmd.isSensitiveCommand(command)):
            command = command if userConfirmsCommandExecution(self.rawCommand) else None
        if command is not None:
            print(f"Entered command launched: {self.rawCommand}")
            print("-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-")
            result = self.__executeCommand__(command)
            print("-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-")
            print("Entered command finished! (or is running in the background) Scroll up to check output (if any) if it exceeds the screen.")
        else:
            self.rawCommand = ""
        return result

    """ execute (repeat) previous command """
    def executePreviousCommand(self):
        result = None
        if len(self.previousCommand) > 0:
            command = self.__expandCommand__(self.previousCommand)
            if (cmd.isSensitiveCommand(command)):
                command = command if userConfirmsCommandExecution(self.rawCommand) else None
            if command is not None:
                print(f"Repeated command launched: {self.rawCommand}")
                print("-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-")
                result = self.__executeCommand__(command)
                print("-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-")
                print("Repeated command finished! (or is running in the background) Scroll up to check output (if any) if it exceeds the screen.")
            else:
                self.rawCommand = ""
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
            out.printFallbackMessage()
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
                commandToExecute = self.__expandCommand__(commandsHistoryEntry)
                if cmd.isSensitiveCommand(commandToExecute):
                    commandToExecute = commandToExecute if userConfirmsCommandExecution(self.rawCommand) else None
                if commandToExecute is not None:
                    print(f"Repeated command launched: {self.rawCommand}")
                    print("-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-")
                    commandExecStatus, passedCommandExecInput, passedCommandExecOutput = self.__executeCommand__(commandToExecute)
                    print("-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-")
                    print("Repeated command finished! (or is running in the background) Scroll up to check output (if any) if it exceeds the screen.")
                else:
                    self.rawCommand = ""
                    commandExecStatus = 2
                    status = commandExecStatus
            else:
                commandExecStatus, passedCommandExecInput, passedCommandExecOutput = self.__editAndExecuteCommand__(commandsHistoryEntry)
                if commandExecStatus != 0:
                    status = 2 #aborted by user
            passedInput = passedCommandExecInput
        return (status, passedInput, "")

    """ interactive menu for entering aliases """
    def visitAliasesMaintenanceMenu(self):
        def promptUserToSaveAliasUpdates():
            os.system("clear")
            addedAliases, modifiedAliases, removedAliases = self.cmd.getPendingAliasesUpdates()
            if len(addedAliases) > 0:
                print("Added aliases: ")
                for alias, aliasContent in addedAliases.items():
                    print(f"{alias}=\'{aliasContent}\'")
                print("")
            if len(modifiedAliases) > 0:
                print("Modified aliases: ")
                for alias, aliasContent in modifiedAliases.items():
                    print(f"{alias}=\'{aliasContent}\'")
                print("")
            if len(removedAliases) > 0:
                print("Removed aliases: ")
                for alias in removedAliases:
                    print(f"\'{alias}\'")
                print("")
            print("Do you want to save the changes?")
            print("")
            choice = common.getInputWithTextCondition("Enter your choice (y/n): ", lambda userInput: userInput.lower() not in {'y', 'n'}, \
                                                  "Invalid choice selected. Please try again")
            return choice.lower() == "y"
        self.cmd.refreshAliases()
        print("Welcome to interactive menu for entering aliases!")
        print("")
        userFinishedEnteringAliases = False
        while not userFinishedEnteringAliases:
            print("Enter alias (press ENTER to abort): ")
            alias = input()
            alias = alias.strip().lower()
            if len(alias) > 0:
                if not cmd.isValidAlias(alias):
                    os.system("clear")
                    print("Invalid alias! It should only contain alphanumeric characters! Please try again")
                    print("")
                    continue
                print("Enter alias content (press ENTER to remove an existing alias): ")
                aliasContent = input()
                aliasContent = aliasContent.strip()
                os.system("clear")
                if len(aliasContent) > 0:
                    addedOrModified = self.cmd.addOrModifyAlias(alias, aliasContent)
                    if addedOrModified:
                        print(f"Alias \'{alias}\' marked for adding/modifying, content is: \'{aliasContent}\'!")
                    else:
                        print(f"Alias \'{alias}\' already exists with content \'{aliasContent}\', any previous modification request cancelled!")
                else:
                    removed = self.cmd.removeAlias(alias)
                    if removed:
                        print(f"Alias \'{alias}\' marked for removal!")
                    else:
                        print(f"Alias \'{alias}\' doesn't exist, nothing to remove (any previous adding request cancelled)!")
                print("")
            else:
                userFinishedEnteringAliases = True
        if self.cmd.areAliasesUpdatesPending():
            shouldChangesBeSaved = promptUserToSaveAliasUpdates()
            self.cmd.handleUpdatingAliasesFinished(shouldChangesBeSaved)
            os.system("clear")
            print("Alias changes saved!") if shouldChangesBeSaved else print("Alias changes aborted!")
        else:
            os.system("clear")
            print("You exited aliases menu!")
        syncedCurrentDir, fallbackPerformed = sysfunc.syncCurrentDir() # handle the case when current dir became unavailable while in aliases menu
        if fallbackPerformed:
            print("")
            print("Current directory no longer reachable (probably deleted). It has been replaced by fallback directory.")
            print("Please resume operations by considering the new current directory.")

    def displayAliases(self):
        self.cmd.refreshAliases()
        aliases = self.cmd.getAliases()
        if len(aliases) > 0:
            print("Available aliases: ")
            print("")
            for alias, aliasContent in aliases:
                print(f"alias {alias}=\'{aliasContent}\'")
            print("")
            print("Scroll up (if needed) to check all aliases.")
        else:
            print("There are no aliases!")

    """ resets the commands history """
    def clearCommandsHistory(self):
        self.cmd.clearHistory()
        print("Content of commands history menu has been erased.")

    """ quick commands history is part of recent history but can be accessed outside the regular history menus """
    def displayQuickCommandsHistory(self):
        (consolidatedHistory, recentHistoryEntriesCount) = self.cmd.getHistoryInfo()
        if recentHistoryEntriesCount > 0:
            assert cmdset.q_hist_max_entries > 0, "Invalid quick navigation history maximum entries count"
            recentHistory = consolidatedHistory[0: recentHistoryEntriesCount]
            self.__displayFormattedCmdFileContent__(recentHistory, 0, cmdset.q_hist_max_entries)
        else:
            print("No commands recently executed!")

    """ checks the entry number is a positive integer belonging to the range of entries contained in quick history (subset of recent commands history) """
    def isValidQuickCmdHistoryEntryNr(self, userInput):
        return self.cmd.isValidQuickHistoryEntryNr(userInput)

    """ checks if the consolidated commands history is empty """
    def isCommandsHistoryEmpty(self):
        return self.cmd.isHistoryMenuEmpty()

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
            out.printFallbackMessage()
        elif commandLength > 0 and commandToExecute[commandLength-1] != ':':
            commandToExecute = self.__expandCommand__(commandToExecute)
            if (cmd.isSensitiveCommand(commandToExecute)):
                commandToExecute = commandToExecute if userConfirmsCommandExecution(self.rawCommand) else None
            if commandToExecute is not None:
                commandType = "Edited" if previousCommand != "" else "Entered"
                print(f"{commandType} command launched: {self.rawCommand}")
                print("-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-")
                commandExecStatus, passedCommandExecInput, passedCommandExecOutput = self.__executeCommand__(commandToExecute)
                print("-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-")
                print(f"{commandType} command finished! (or is running in the background) Scroll up to check output (if any) if it exceeds the screen.")
                passedInput = passedCommandExecInput
            else:
                self.rawCommand = ""
                status = 2 # sensitive command aborted by user
        else:
            print("Command aborted. You returned to navigation menu.")
            status = 2 #aborted by user
        return (status, passedInput, "")

    """ function that expands the command before executing (in case it has aliases) """
    def __expandCommand__(self, command):
        self.rawCommand = command # keep original command for storing in history
        expandedCommand = self.cmd.expandCommand(self.rawCommand) # check for aliases and expand the command if required
        return expandedCommand

    """ core command execution function """
    def __executeCommand__(self, command):
        assert len(command) > 0, "Empty command has been provided"
        os.system(command)
        if len(self.rawCommand) >= cmd.getMinCommandSize():
            self.cmd.updateHistory(self.rawCommand)
        self.previousCommand = self.rawCommand
        self.rawCommand = ""
        return (0, self.previousCommand, "")

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

def userConfirmsCommandExecution(command):
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
    shouldCommandBeExecuted = choice.lower() == "y"
    if not shouldCommandBeExecuted:
        print("Command aborted. You returned to navigation menu.")
    return shouldCommandBeExecuted
