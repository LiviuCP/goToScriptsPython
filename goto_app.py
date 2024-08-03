import os
import navigation as nav, commands as cmd, common, clipboard as clip, recursive_transfer as rt, rename as rn, system_functionality as sysfunc, display as out

renaming_commands = {"ra", "ran", "rp", "rpn", "ri", "rin", "rd", "rr", "rrn"}
renaming_translations = {"ra" : "a", "ran" : "A", "rp" : "p", "rpn" : "P", "ri" : "i", "rin" : "I", "rd" : "d", "rr" : "r", "rrn" : "R"}
contexts_dict = {":<" : "--execute", "::" : "--edit", "<" : "-h", "<<" : "-fh", ">" : "-f", ">>" : "-ff", "main" : ""}
valid_contexts = {"--execute", "--edit", "-h", "-fh", "-f", "-ff", ""}
context_switch_dict = {"--execute" : "--edit", "--edit" : "--execute", "-f" : "-h", "-h" : "-f", "-fh" : "-ff", "-ff" : "-fh", "" : ""}

''' status/action codes: -1 - goTo not successfully executed, 0 - no action performed (default), 1 - input to be forwarded to BASH, 2 - previous command and command result to be updated, 3 - no arguments, 4 - update previous directory and cd '''
class Application:
    def __init__(self):
        self.currentContext = "" # main context
        self.currentFilter = "" # should change to a non-empty value each time the user filters the navigation/command history (otherwise it should be reset to an empty value)
        syncedCurrentDir, fallbackPerformed = sysfunc.syncCurrentDir() # TODO: at next refactoring phase check if status code should remain 0 for fallback or a dedicated status code should be chosen (maybe 5?)
        self.nav = nav.Navigation(syncedCurrentDir)
        self.cmd = cmd.Commands()
        self.clipboard = clip.Clipboard()
        self.recursiveTransfer = rt.RecursiveTransfer()
        self.appStatus = 0
        self.passedInput = ""
        self.isQuickHistEnabled = False
        common.setPathAutoComplete()

    def execute(self):
        userInput = ""
        keyInterruptOccurred = False
        os.system("clear")
        print("Welcome to navigation app!")
        self.nav.initSyncWithFinder()
        while userInput != "!" and not keyInterruptOccurred:
            self.nav.checkSyncWithFinder()
            if userInput not in {"?", "?clip", "?ren"}:
                self.__displayGeneralOutput__()
            try:
                userInput = input()
                userInput = userInput.strip(' ') #there should be no trailing spaces, otherwise the entries might get duplicated in the navigation/command history or other errors might occur (depending on input use case)
                self.__handleUserInput__(userInput)
                while self.appStatus == 1:
                    userInput = self.passedInput
                    self.__handleUserInput__(userInput)
            except (KeyboardInterrupt, EOFError): # CTRL + C, CTRL + D (latter one causes EOFError)
                keyInterruptOccurred = True
                self.__handleCloseApplication__(self.cmd.getPreviousCommand())

    def __handleUserInput__(self, userInput):
        #any input starting with < and continuing with a character different from < is considered a quick navigation history request (no matter if valid or not, e.g. <a is invalid)
        def isQuickNavigationRequested(userInput):
            userInput = userInput.strip(' ')
            isQuickNavHistInput = len(userInput) > 1 and ((userInput[0] == "<" and userInput[1] != "<") or userInput[0:2] == ",,")
            return isQuickNavHistInput
        #any input starting with "-" and not starting with "->" is considered a quick commands history request (no matter if valid or not, e.g. -a is invalid)
        def isQuickCommandRequested(userInput):
            userInput = userInput.strip(' ')
            isQuickCmdHistInput = len(userInput) > 1 and userInput[0] == "-" and userInput[1] != ">"
            return isQuickCmdHistInput
        def isSwitchToMainContextRequired(appExecInfo):
            isSwitchRequired = True
            if appExecInfo is not None:
                appExecStatus, appExecPassedInput, appExecPassedOutput = appExecInfo
                isSwitchRequired = appExecStatus != 1 or (appExecPassedInput != ":t" and not (isQuickNavigationRequested(appExecPassedInput) or isQuickCommandRequested(appExecPassedInput)))
            return isSwitchRequired
        def computeNewAppStatus(appExecInfo, currentStatus, requiredNewStatus = -1, checkInputForwarding = False):
            resultingStatus = currentStatus
            if appExecInfo is not None:
                status, passedInput, passedOutput = appExecInfo
                if checkInputForwarding:
                    if status == 1:
                        resultingStatus = status
                elif status == 0:
                    resultingStatus = requiredNewStatus
            return resultingStatus
        os.system("clear")
        self.appStatus = 0
        self.passedInput = ""
        shouldSwitchToMainContext = True
        result = None # a valid result should contain: (status code, passed input, passed output)
        syncedCurrentDir = "" # actually not used, just for tuple unpacking (see below)
        fallbackPerformed = False
        if userInput not in ["!", "?", "?ren", "?clip"]:
            syncedCurrentDir, fallbackPerformed = sysfunc.syncCurrentDir()
        if fallbackPerformed:
            out.printFallbackMessage()
            self.__handleFallbackPerformed__()
        elif len(userInput) >= 2 and userInput[0:2] in ["<<", ">>"]:
            result = self.__setContext__(contexts_dict[userInput[0:2]], userInput[2:])
            #return to main context only if the user hasn't chosen to toggle or no quick navigation/command has been attempted (same for the below cases)
            shouldSwitchToMainContext = isSwitchToMainContextRequired(result)
        elif len(userInput) >= 1 and userInput[0] == ">":
            navHistInput = userInput[1:].lstrip(' ')
            isInputOk = True
            if len(navHistInput) > 0:
                isInputOk = self.nav.isValidFavoritesEntryNr(navHistInput)
                if not isInputOk:
                    print("Invalid favorites entry number!")
            if isInputOk:
                result = self.__setContext__(contexts_dict[userInput[0]], navHistInput)
                shouldSwitchToMainContext = isSwitchToMainContextRequired(result)
        elif len(userInput) >= 1 and userInput[0] == "<":
            navHistInput = userInput[1:]
            isInputOk = True
            if len(navHistInput) > 0:
                isInputOk = self.__isQuickNavigationPossible__(navHistInput)
            if isInputOk:
                result = self.__setContext__(contexts_dict[userInput[0]], navHistInput)
                shouldSwitchToMainContext = isSwitchToMainContextRequired(result)
        elif userInput in [":n", ":N"]:
            prevNavigationFilter = self.nav.getPreviousNavigationFilter()
            if len(prevNavigationFilter) > 0:
                contexts_dictKey = "<<" if userInput == ":n" else ">>"
                result = self.__setContext__(contexts_dict[contexts_dictKey], prevNavigationFilter)
                shouldSwitchToMainContext = isSwitchToMainContextRequired(result)
            else:
                print("No navigation filter previously entered.")
        elif len(userInput) >= 2 and userInput[0:2] == ",,":
            navHistInput = userInput[2:]
            if self.__isQuickNavigationPossible__(navHistInput):
                result = self.__setContext__(contexts_dict["<"], "," + navHistInput)
                shouldSwitchToMainContext = isSwitchToMainContextRequired(result)
        elif len(userInput) >= 2 and userInput[0:2] in [":<", "::"]:
            result = self.__setContext__(contexts_dict[userInput[0:2]], userInput[2:])
            shouldSwitchToMainContext = isSwitchToMainContextRequired(result)
        elif userInput in [":f", ":F"]:
            prevCommandsFilter = self.cmd.getPreviousCommandsFilter()
            if len(prevCommandsFilter) > 0:
                contexts_dictKey = ":<" if userInput == ":f" else "::"
                result = self.__setContext__(contexts_dict[contexts_dictKey], prevCommandsFilter)
                shouldSwitchToMainContext = isSwitchToMainContextRequired(result)
            else:
                print("No commands filter previously entered.")
        elif userInput == ":t":
            newContext = context_switch_dict[self.currentContext]
            if len(newContext) > 0:
                result = self.__setContext__(newContext, self.currentFilter)
                shouldSwitchToMainContext = isSwitchToMainContextRequired(result)
            else:
                print("Unable to toggle, not in the right menu!")
        elif userInput == ",":
            result = self.nav.goToPreviousDirectory()
            self.appStatus = computeNewAppStatus(result, self.appStatus, 4)
        elif len(userInput) >= 1 and userInput[0] == ";":
            ancestorDirPath = common.computeAncestorDirRelativePath(userInput[1:])
            if len(ancestorDirPath) > 0:
                result = self.nav.goTo(ancestorDirPath)
                self.appStatus = computeNewAppStatus(result, self.appStatus, 4)
            else:
                print("Invalid ancestor directory data provided!")
                print("")
                print("A single ';' character followed by a positive integer (ancestor depth) is required for determining the ancestor directory path.")
                print("No other character types are allowed.")
        elif userInput == ":-":
            result = self.cmd.executePreviousCommand()
            # force updating previous command and its finishing status (although command is just repeated); the command might for example finish with errors although when previously executed it finished successfully (e.g. when removing a file and then attempting to remove it again)
            self.appStatus = computeNewAppStatus(result, self.appStatus, 2)
        elif userInput == ":":
            result = self.cmd.editAndExecutePreviousCommand()
            self.appStatus = computeNewAppStatus(result, self.appStatus, 2)
        elif userInput == "+>":
            self.nav.addDirToFavorites()
        elif userInput == "->":
            result = self.nav.removeDirFromFavorites()
            self.appStatus = computeNewAppStatus(result, self.appStatus, checkInputForwarding = True)
        elif len(userInput) > 1 and userInput[0] in ['-', '+'] and userInput[1] != '>':
            cmdHistInput = userInput[1:]
            if self.__isQuickCommandPossible__(cmdHistInput):
                contextsDictKey = ":<" if userInput[0] == '-' else "::"
                result = self.__setContext__(contexts_dict[contextsDictKey],  cmdHistInput)
                shouldSwitchToMainContext = isSwitchToMainContextRequired(result)
        elif userInput in [":clearnavigation", ":clearcommands"]:
            self.__handleClearHistory__(userInput)
        elif userInput in [":c", ":m", ":y", ":ec", ":dc"]:
            self.__handleClipboardInput__(userInput)
        elif userInput in [":td", ":M", ":C", ":etd", ":dtd"]:
            self.__handleRecursiveTransferInput__(userInput)
        elif userInput == ":a":
            self.cmd.visitAliasesMaintenanceMenu()
        elif userInput == ":A":
            self.cmd.displayAliases()
        elif userInput.startswith(":") and userInput[1:] in renaming_commands:
            rn.rename(renaming_translations[userInput[1:]])
        elif len(userInput) > 1 and userInput[len(userInput)-1] == ":":
            print("Input cancelled, no action performed!")
        elif userInput == ":q":
            if self.__isHistoryEmpty__():
                print("Cannot open quick history! There are no navigation or commands history entries.")
            else:
                self.__toggleQuickHistory__()
        elif userInput in ["?", "?clip", "?ren"]:
            self.__handleHelpRequest__(userInput, out)
        elif userInput == ":s":
            self.nav.toggleSyncWithFinder()
        elif userInput == "!":
            self.__handleCloseApplication__(self.cmd.getPreviousCommand())
        else:
            if len(userInput) > 0 and userInput[0] == ":":
                result = self.cmd.executeCommand(userInput[1:])
                self.appStatus = 2
            else:
                result = self.nav.goTo(userInput)
                self.appStatus = computeNewAppStatus(result, self.appStatus, 4)
        if result is not None:
            self.passedInput = result[1]
        if shouldSwitchToMainContext:
            self.__setContext__(contexts_dict["main"], "")

    def __handleClipboardInput__(self, clipboardInput):
        if clipboardInput == ":c":
            self.clipboard.createAction()
        elif clipboardInput == ":m":
            self.clipboard.createAction(False)
        elif clipboardInput == ":y":
            self.clipboard.applyAction()
        elif clipboardInput == ":ec":
            self.clipboard.erase(True)
        elif clipboardInput == ":dc":
            self.clipboard.display()
        else:
            assert False, "Invalid clipboard option"

    def __handleRecursiveTransferInput__(self, recursiveTransferInput):
        if recursiveTransferInput == ":td":
            self.recursiveTransfer.setTargetDir()
        elif recursiveTransferInput == ":M":
            self.recursiveTransfer.transferItemsToTargetDir(False)
        elif recursiveTransferInput == ":C":
            self.recursiveTransfer.transferItemsToTargetDir()
        elif recursiveTransferInput == ":etd":
            self.recursiveTransfer.eraseTargetDir(True)
        elif recursiveTransferInput == ":dtd":
            self.recursiveTransfer.displayTargetDir()
        else:
            assert False, "Invalid recursive transfer option"

    def __handleClearHistory__(self, keyword):
        assert keyword in [":clearnavigation", ":clearcommands"]
        print(f"Are you sure you want to clear the {keyword[6:]} history?")
        choice = common.getInputWithTextCondition("Enter your choice (y/n): ", lambda userInput: userInput.lower() not in {'y', 'n'}, \
                                              "Invalid choice selected. Please try again")
        os.system("clear")
        if choice.lower() == "n":
            print("Aborted")
        else:
            self.nav.clearVisitedDirsMenu() if keyword == ":clearnavigation" else self.cmd.clearCommandsHistory()
            if self.isQuickHistEnabled and self.__isHistoryEmpty__():
                self.__toggleQuickHistory__()

    ''' Contexts are related to main menus:
        - navigation history
        - filtered navigation history
        - favorites
        - command history in execute mode (filtered or not)
        - command history in edit mode (filtered or not)
        - main navigation mode (no main menu): includes all sub-contexts: edit an individual command, help menu, move/copy, recursive move/copy, renaming files/dirs etc '''
    def __setContext__(self, newContext, userInput):
        assert newContext in valid_contexts, "Invalid context detected"
        if len(self.currentFilter) > 0:
            assert self.currentContext in ["-fh", "-ff", "--execute", "--edit"], "Invalid filter keyword within current context"
        self.currentContext = newContext
        self.currentFilter = ""
        status = None
        passedInput = ""
        passedOutput = ""
        if self.currentContext in ["--execute", "--edit"]:
            if not self.__isQuickCommandPossible__(userInput):
                self.currentFilter = userInput
            status, passedInput, passedOutput = self.cmd.visitCommandsMenu(self.currentContext, userInput)
            self.appStatus = 2 if status == 0 else 1 if status == 1 else self.appStatus
        elif self.currentContext in ["-f", "-h"]:
            status, passedInput, passedOutput = self.nav.executeGoToFromMenu(self.currentContext, userInput, self.cmd.getPreviousCommand())
            if len(userInput) > 0:
                self.appStatus = 4 if status == 0 else 1 if status in [1, 4] else self.appStatus #forward user input if history menu is empty and the user enters <[entry_nr] (status == 4)
            else:
                self.appStatus = 4 if status <= 0 else 1 if status == 1 else self.appStatus
                if status == -1:
                    self.recursiveTransfer.setTargetDir(passedInput)
        elif self.currentContext in ["-fh", "-ff"]:
            if len(userInput) > 0:
                self.currentFilter = userInput
                status, passedInput, passedOutput = self.nav.executeGoToFromMenu(self.currentContext, userInput, self.cmd.getPreviousCommand())
                self.appStatus = 4 if status <= 0 else 1 if status == 1 else self.appStatus
                if status == -1:
                    self.recursiveTransfer.setTargetDir(passedInput)
            else:
                print("No filter keyword entered. Cannot filter ", end='')
                print("navigation history.") if self.currentContext == "-fh" else print("favorites.")
        result = (status, passedInput, passedOutput) if status is not None else None
        return result

    def __handleFallbackPerformed__(self):
        self.clipboard.erase()
        self.recursiveTransfer.eraseTargetDir()

    def __toggleQuickHistory__(self):
        self.isQuickHistEnabled = not self.isQuickHistEnabled
        print("Quick history enabled!") if self.isQuickHistEnabled else print("Quick history disabled!")

    def __isQuickNavigationPossible__(self, navHistInput):
        isQuickNavPossible = False
        if len(self.currentContext) > 0: #quick history is only accessible from main navigation page (excluding help menus) - it should be visible when accessed!
            print("Quick history not accessible from current context. Please try again!")
        elif self.isQuickHistEnabled:
            if self.nav.isValidQuickNavHistoryEntryNr(navHistInput):
                isQuickNavPossible = True
            else:
                print("Invalid quick navigation history entry number! Please try again.")
        else:
            print("Quick history is disabled. Please enable it and try again!")
        return isQuickNavPossible

    def __isQuickCommandPossible__(self, cmdHistInput):
        isQuickCmdPossible = False
        if len(self.currentContext) > 0: #quick history is only accessible from main navigation page (excluding help menus) - it should be visible when accessed!
            print("Quick history not accessible from current context. Please try again!")
        elif self.isQuickHistEnabled:
            if self.cmd.isValidQuickCmdHistoryEntryNr(cmdHistInput):
                isQuickCmdPossible = True
            else:
                print("Invalid quick commands history entry number! Please try again.")
        else:
            print("Quick history is disabled. Please enable it and try again!")
        return isQuickCmdPossible

    def __handleHelpRequest__(self, helpInput, out):
        syncedCurrentDir, fallbackPerformed = sysfunc.syncCurrentDir()
        if helpInput in ["?", "?clip", "?ren"]:
            os.system("clear")
            if self.isQuickHistEnabled:
                self.__toggleQuickHistory__()
                print("----------------------------------")
        else:
            assert False, "Invalid help option"
        if helpInput == "?":
            out.displayGeneralHelp(syncedCurrentDir, fallbackPerformed)
        elif helpInput == "?clip":
            out.displayClipboardHelp(syncedCurrentDir, fallbackPerformed)
        else:
            out.displayRenamingHelp(syncedCurrentDir, fallbackPerformed)
        out.displayHelpMenuFooter()

    def __handleCloseApplication__(self, previousCommand):
        navModifiedByPreviousSession = self.nav.closeNavigation()
        cmdModifiedByPreviousSession = self.cmd.closeCommands()
        os.system("clear")
        print("You exited the navigation app.")
        print("")
        if navModifiedByPreviousSession or cmdModifiedByPreviousSession:
            print("The navigation and/or commands environment had been modified by a previous script session.")
            print("All modifications have been reconciled.")
            print("")
        syncedCurrentDir, fallbackPerformed = sysfunc.syncCurrentDir()
        out.printCurrentDir(syncedCurrentDir, fallbackPerformed, "Last visited")
        print("Last executed shell command: ", end='')
        print(previousCommand) if len(previousCommand) > 0 else print("none")
        print("")

    def __displayGeneralOutput__(self):
        syncedCurrentDir, fallbackPerformed = sysfunc.syncCurrentDir()
        assert not fallbackPerformed, "Current dir fallback not allowed, should have already been performed!"
        prevCommand = self.cmd.getPreviousCommand()
        out.displayGeneralOutputUpperSection(syncedCurrentDir, self.nav.getPreviousDirectory())
        if self.isQuickHistEnabled:
            self.__displayQuickHistory__()
        out.displayGeneralOutputLowerSection(prevCommand, self.nav.getPreviousNavigationFilter(), self.cmd.getPreviousCommandsFilter(), self.clipboard.getActionLabel(), self.clipboard.getKeyword(), self.clipboard.getSourceDir(), self.recursiveTransfer.getTargetDir(), self.nav.isSyncWithFinderEnabled())

    def __displayQuickHistory__(self):
        print("---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
        print("")
        print("Recently visited directories (home directory excluded):")
        print("")
        self.nav.displayQuickNavigationHistory()
        print("")
        print("---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
        print("")
        print("Recently executed commands (short commands excluded):")
        print("")
        self.cmd.displayQuickCommandsHistory()
        print("")

    def __isHistoryEmpty__(self):
        return self.nav.isNavigationHistoryEmpty() and self.cmd.isCommandsHistoryEmpty()

application = Application()
application.execute()
