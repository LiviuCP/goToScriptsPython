import os
import navigation as nav, quick_navigation as qnav, commands as cmd, common, clipboard as clip, recursive_transfer as rt, rename as rn, system_functionality as sysfunc, display as out

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
        syncResult = sysfunc.syncCurrentDir() # TODO: at next refactoring phase check if status code should remain 0 for fallback or a dedicated status code should be chosen (maybe 5?)
        self.nav = nav.Navigation(syncResult[0])
        self.cmd = cmd.Commands()
        self.clipboard = clip.Clipboard()
        self.recursiveTransfer = rt.RecursiveTransfer()
        self.appStatus = 0
        self.passedInput = ""
        self.isQuickNavHistEnabled = False
        common.setPathAutoComplete()

    def execute(self):
        userInput = ""
        keyInterruptOccurred = False
        os.system("clear")
        print("Welcome to navigation app!")
        while userInput is not "!" and not keyInterruptOccurred:
            prevCommand = self.cmd.getPreviousCommand()
            if userInput not in {"?", "?clip", "?ren"}:
                if len(prevCommand) > 0:
                    prevCommandFinishingStatus = "successfully" if self.cmd.getPreviousCommandSuccess() else "with errors"
                    out.displayGeneralOutput(self.nav.getPreviousDirectory(), prevCommand, prevCommandFinishingStatus, self.nav.getPreviousNavigationFilter(), self.cmd.getPreviousCommandsFilter(), self.clipboard.getActionLabel(), self.clipboard.getKeyword(), self.clipboard.getSourceDir(), self.recursiveTransfer.getTargetDir(), self.isQuickNavHistEnabled)
                else:
                    out.displayGeneralOutput(self.nav.getPreviousDirectory(), navigationFilter = self.nav.getPreviousNavigationFilter(), commandsFilter = self.cmd.getPreviousCommandsFilter(), clipboardAction = self.clipboard.getActionLabel(), clipboardKeyword = self.clipboard.getKeyword(), clipboardSourceDir = self.clipboard.getSourceDir(), recursiveTargetDir = self.recursiveTransfer.getTargetDir(), isQuickNavHistEnabled = self.isQuickNavHistEnabled)
            try:
                userInput = input()
                userInput = userInput.strip(' ') #there should be no trailing spaces, otherwise the entries might get duplicated in the navigation/command history or other errors might occur (depending on input use case)
                self.__handleUserInput(userInput)
                while self.appStatus == 1:
                    userInput = self.passedInput
                    self.__handleUserInput(userInput)
            except (KeyboardInterrupt, EOFError): # CTRL + C, CTRL + D (latter one causes EOFError)
                keyInterruptOccurred = True
                self.__handleCloseApplication(prevCommand)

    def __handleUserInput(self, userInput):
        #any input starting with < and continuing with a character different from < is considered a quick navigation history request (no matter if valid or not, e.g. <a is invalid)
        def isQuickNavigationRequested(userInput):
            userInput = userInput.strip(' ')
            isQuickNavHistInput = len(userInput) > 1 and ((userInput[0] == "<" and userInput[1] != "<") or userInput[0:2] == ",,")
            return isQuickNavHistInput
        os.system("clear")
        self.appStatus = 0
        self.passedInput = ""
        shouldSwitchToMainContext = True
        result = None # a valid result should contain: (status code, passed input, passed output)
        fallbackPerformed = False
        if userInput not in ["!", "?", "?ren", "?clip"]:
            syncResult = sysfunc.syncCurrentDir()
            fallbackPerformed = syncResult[1]
        if fallbackPerformed:
            out.printFallbackMessage()
            self.__handleFallbackPerformed()
        elif len(userInput) >= 2 and userInput[0:2] in ["<<", ">>"]:
            result = self.__setContext(contexts_dict[userInput[0:2]], userInput[2:])
            #return to main context only if the user hasn't chosen to toggle or no quick navigation has been attempted (same for the below cases)
            shouldSwitchToMainContext = (result is  None) or (result[0] != 1) or (result[1] != ":t" and not isQuickNavigationRequested(result[1]))
        elif len(userInput) >= 1 and userInput[0] == ">":
            navHistInput = userInput[1:].lstrip(' ')
            isInputOk = True
            if len(navHistInput) > 0:
                isInputOk = nav.isValidFavoritesEntryNr(navHistInput)
                if not isInputOk:
                    print("Invalid favorites entry number!")
            if isInputOk:
                result = self.__setContext(contexts_dict[userInput[0]], navHistInput)
                shouldSwitchToMainContext = (result is  None) or (result[0] != 1) or (result[1] != ":t" and not isQuickNavigationRequested(result[1]))
        elif len(userInput) >= 1 and userInput[0] == "<":
            navHistInput = userInput[1:]
            isInputOk = True
            if len(navHistInput) > 0:
                isInputOk = self.__isQuickNavigationPossible(navHistInput)
            if isInputOk:
                result = self.__setContext(contexts_dict[userInput[0]], navHistInput)
                shouldSwitchToMainContext = (result is  None) or (result[0] != 1) or (result[1] != ":t" and not isQuickNavigationRequested(result[1]))
        elif userInput in [":n", ":N"]:
            prevNavigationFilter = self.nav.getPreviousNavigationFilter()
            if len(prevNavigationFilter) > 0:
                contexts_dictKey = "<<" if userInput == ":n" else ">>"
                result = self.__setContext(contexts_dict[contexts_dictKey], prevNavigationFilter)
                shouldSwitchToMainContext = (result is  None) or (result[0] != 1) or (result[1] != ":t" and not isQuickNavigationRequested(result[1]))
            else:
                print("No navigation filter previously entered.")
        elif len(userInput) >= 2 and userInput[0:2] == ",,":
            navHistInput = userInput[2:]
            if self.__isQuickNavigationPossible(navHistInput):
                result = self.__setContext(contexts_dict["<"], "," + navHistInput)
                shouldSwitchToMainContext = (result is  None) or (result[0] != 1) or (result[1] != ":t" and not isQuickNavigationRequested(result[1]))
        elif len(userInput) >= 2 and userInput[0:2] in [":<", "::"]:
            result = self.__setContext(contexts_dict[userInput[0:2]], userInput[2:])
            shouldSwitchToMainContext = (result is  None) or (result[0] != 1) or (result[1] != ":t" and not isQuickNavigationRequested(result[1]))
        elif userInput in [":f", ":F"]:
            prevCommandsFilter = self.cmd.getPreviousCommandsFilter()
            if len(prevCommandsFilter) > 0:
                contexts_dictKey = ":<" if userInput == ":f" else "::"
                result = self.__setContext(contexts_dict[contexts_dictKey], prevCommandsFilter)
                shouldSwitchToMainContext = (result is  None) or (result[0] != 1) or (result[1] != ":t" and not isQuickNavigationRequested(result[1]))
            else:
                print("No commands filter previously entered.")
        elif userInput == ":t":
            newContext = context_switch_dict[self.currentContext]
            if len(newContext) > 0:
                result = self.__setContext(newContext, self.currentFilter)
                shouldSwitchToMainContext = (result is  None) or (result[0] != 1) or (result[1] != ":t" and not isQuickNavigationRequested(result[1]))
            else:
                print("Unable to toggle, not in the right menu!")
        elif userInput == ",":
            result = self.nav.goToPreviousDirectory()
            self.appStatus = 4 if result[0] == 0 else self.appStatus
        elif len(userInput) >= 1 and userInput[0] == ";":
            ancestorDirPath = common.computeAncestorDirRelativePath(userInput[1:])
            if len(ancestorDirPath) > 0:
                result = self.nav.goTo(ancestorDirPath)
                self.appStatus = 4 if result[0] == 0 else self.appStatus
            else:
                print("Invalid ancestor directory data provided!")
                print("")
                print("A single ';' character followed by a positive integer (ancestor depth) is required for determining the ancestor directory path.")
                print("No other character types are allowed.")
        elif userInput == ":-":
            result = self.cmd.executePreviousCommand()
            if result is not None:
                self.appStatus = 2 if result[0] == 0 else self.appStatus # force updating previous command and its finishing status (although command is just repeated); the command might for example finish with errors although when previously executed it finished successfully (e.g. when removing a file and then attempting to remove it again)
        elif userInput == ":":
            result = self.cmd.editAndExecutePreviousCommand()
            self.appStatus = 2 if result[0] == 0 else self.appStatus
        elif userInput == "+>":
            nav.addDirToFavorites()
        elif userInput == "->":
            result = nav.removeDirFromFavorites()
            self.appStatus = 1 if result[0] == 1 else self.appStatus
        if userInput == ":clearnavigation":
            nav.clearVisitedDirsMenu()
        elif userInput == ":clearcommands":
            cmd.clearCommandHistory()
        elif userInput in [":c", ":m", ":y", ":ec", ":dc"]:
            self.__handleClipboardInput(userInput)
        elif userInput in [":td", ":M", ":C", ":etd", ":dtd"]:
            self.__handleRecursiveTransferInput(userInput)
        elif userInput.startswith(":") and userInput[1:] in renaming_commands:
            rn.rename(renaming_translations[userInput[1:]])
        elif len(userInput) > 1 and userInput[len(userInput)-1] == ":":
            print("Input cancelled, no action performed!")
        elif userInput == ":qn":
            self.__toggleQuickNavigationHistory()
        elif userInput in ["?", "?clip", "?ren"]:
            self.__handleHelpRequest(userInput, out)
        elif userInput == "!":
            self.__handleCloseApplication(self.cmd.getPreviousCommand())
        else:
            if len(userInput) > 0 and userInput[0] == ":":
                result = self.cmd.executeCommand(userInput[1:])
                self.appStatus = 2
            else:
                result = self.nav.goTo(userInput)
                self.appStatus = 4 if result[0] == 0 else self.appStatus
        if result is not None:
            self.passedInput = result[1]
        if shouldSwitchToMainContext:
            self.__setContext(contexts_dict["main"], "")

    def __handleClipboardInput(self, clipboardInput):
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

    def __handleRecursiveTransferInput(self, recursiveTransferInput):
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

    ''' Contexts are related to main menus:
        - navigation history
        - filtered navigation history
        - favorites
        - command history in execute mode (filtered or not)
        - command history in edit mode (filtered or not)
        - main navigation mode (no main menu): includes all sub-contexts: edit an individual command, help menu, move/copy, recursive move/copy, renaming files/dirs etc '''
    def __setContext(self, newContext, userInput):
        assert newContext in valid_contexts, "Invalid context detected"
        if len(self.currentFilter) > 0:
            assert self.currentContext in ["-fh", "-ff", "--execute", "--edit"], "Invalid filter keyword within current context"
        self.currentContext = newContext
        self.currentFilter = ""
        result = None  # a valid result should contain: (status code, passed input, passed output)
        if self.currentContext in ["--execute", "--edit"]:
            self.currentFilter = userInput
            result = self.cmd.visitCommandMenu(self.currentContext, userInput)
            self.appStatus = 2 if result[0] == 0 else 1 if result[0] == 1 else self.appStatus
        elif self.currentContext in ["-f", "-h"]:
            result = self.nav.executeGoToFromMenu(self.currentContext, userInput, self.cmd.getPreviousCommand())
            if len(userInput) > 0:
                self.appStatus = 4 if result[0] == 0 else 1 if (result[0] == 1 or result[0] == 4) else self.appStatus #forward user input if history menu is empty and the user enters <[entry_nr] (result == 4)
            else:
                self.appStatus = 4 if result[0] <= 0 else 1 if result[0] == 1 else self.appStatus
                if result[0] == -1:
                    self.recursiveTransfer.setTargetDir(result[1])
        elif self.currentContext in ["-fh", "-ff"]:
            if len(userInput) > 0:
                self.currentFilter = userInput
                result = self.nav.executeGoToFromMenu(self.currentContext, userInput, self.cmd.getPreviousCommand())
                self.appStatus = 4 if result[0] <= 0 else 1 if result[0] == 1 else self.appStatus
                if result[0] == -1:
                    self.recursiveTransfer.setTargetDir(result[1])
            else:
                print("No filter keyword entered. Cannot filter ", end='')
                print("navigation history.") if self.currentContext == "-fh" else print("favorites.")
        return result

    def __handleFallbackPerformed(self):
        self.clipboard.erase()
        self.recursiveTransfer.eraseTargetDir()

    def __toggleQuickNavigationHistory(self):
        self.isQuickNavHistEnabled = not self.isQuickNavHistEnabled
        print("Quick navigation history enabled!") if self.isQuickNavHistEnabled else print("Quick navigation history disabled!")

    def __isQuickNavigationPossible(self, navHistInput):
        isQuickNavPossible = False
        if len(self.currentContext) > 0: #quick history is only accessible from main navigation page (including help menus) - it should be visible when accessed!
            print("Quick navigation history not accessible from current context. Please try again!")
        elif self.isQuickNavHistEnabled:
            if qnav.isValidEntryNr(navHistInput):
                isQuickNavPossible = True
            else:
                print("Invalid quick history entry number! Please try again.")
        else:
            print("Quick history is disabled. Please enable it and try again!")
        return isQuickNavPossible
    def __handleHelpRequest(self, helpInput, out):
        if helpInput == "?":
            out.displayHelp(self.isQuickNavHistEnabled)
        elif helpInput == "?clip":
            out.displayClipboardHelp(self.isQuickNavHistEnabled)
        elif helpInput == "?ren":
            out.displayRenamingHelp(self.isQuickNavHistEnabled)
        else:
            assert False, "Invalid help option"

    def __handleCloseApplication(self, previousCommand):
        os.system("clear")
        print("You exited the navigation app.")
        print("")
        out.printCurrentDir("Last visited")
        print("Last executed shell command: ", end='')
        print(previousCommand) if len(previousCommand) > 0 else print("none")
        print("")

application = Application()
application.execute()
