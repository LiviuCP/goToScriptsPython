import os
import display as out, navigation as nav, commands as cmd, common, clipboard as clip, recursive_transfer as rt, rename as rn

renaming_commands = {"ra", "ran", "rp", "rpn", "ri", "rin", "rd", "rr", "rrn"}
renaming_translations = {"ra" : "a", "ran" : "A", "rp" : "p", "rpn" : "P", "ri" : "i", "rin" : "I", "rd" : "d", "rr" : "r", "rrn" : "R"}
contexts_dict = {":<" : "--execute", "::" : "--edit", "<" : "-h", "<<" : "-fh", ">" : "-f", ">>" : "-ff", "main" : ""}
valid_contexts = {"--execute", "--edit", "-h", "-fh", "-f", "-ff", ""}
context_switch_dict = {"--execute" : "--edit", "--edit" : "--execute", "-f" : "-h", "-h" : "-f", "-fh" : "-ff", "-ff" : "-fh", "" : ""}

''' status/action codes: -1 - goTo not successfully executed, 0 - no action performed (default), 1 - input to be forwarded to BASH, 2 - previous command and command result to be updated, 3 - no arguments, 4 - update previous directory and cd '''
class Application:
    def __init__(self):
        self.currentContext = "" # main context
        self.currentFilter = "" # should change each time the user filters the navigation/command history
        self.prevNavigationFilter = "" # stores the last navigation filter applied by user
        self.prevCommandsFilter = "" # stores the last commands filter applied by user
        self.prevDir = os.getcwd()
        self.prevCommand = ""
        self.clipboard = clip.Clipboard()
        self.recursiveTransfer = rt.RecursiveTransfer()
        self.status = 0
        self.passedInput = ""
        self.passedOutput = ""
        self.syncWithFinder = False
        common.setPathAutoComplete()
        nav.initNavMenus()
        cmd.initCmdMenus()

    def execute(self):
        commandResult = ""
        userInput = ""
        forwardUserInput = False
        os.system("clear")
        print("Welcome to navigation app!")
        while True:
            if userInput not in {"?", "?clip", "?ren"}:
                if len(self.prevCommand) > 0:
                    out.displayGeneralOutput(self.prevDir, self.syncWithFinder, self.prevCommand, commandResult, self.prevNavigationFilter, self.prevCommandsFilter, self.clipboard.getActionLabel(), self.clipboard.getKeyword(), self.recursiveTransfer.getTargetDir())
                else:
                    out.displayGeneralOutput(self.prevDir, self.syncWithFinder, navigationFilter = self.prevNavigationFilter, commandsFilter = self.prevCommandsFilter, clipboardAction = self.clipboard.getActionLabel(), clipboardKeyword = self.clipboard.getKeyword(), recursiveTargetDir = self.recursiveTransfer.getTargetDir())
            userInput = input()
            userInput = userInput.rstrip(' ') #there should be no trailing spaces, otherwise the entries might get duplicated in the navigation/command history
            while True:
                os.system("clear")
                self.handleUserInput(userInput)
                if self.status == 1:
                    userInput = self.passedInput
                    forwardUserInput = True
                elif self.status == 2:
                    self.prevCommand = self.passedInput
                    commandResult = self.passedOutput
                elif self.status == 4:
                    self.prevDir = self.passedOutput
                if forwardUserInput == True:
                    forwardUserInput = False
                else:
                    break
            if userInput == "!":
                break

    def handleUserInput(self, userInput):
        self.status = 0
        self.passedInput = ""
        self.passedOutput = ""
        shouldSwitchToMainContext = True
        result = None # a valid result should contain: (status code, passed input, passed output)
        if len(userInput) >= 2 and userInput[0:2] in ["<<", ">>"]:
            result = self.setContext(contexts_dict[userInput[0:2]], userInput[2:])
            shouldSwitchToMainContext = (result is  None) or (result[0] != 1) or (result[1] != ":t") #return to main context only if the user hasn't chosen to toggle
        elif len(userInput) >= 1 and userInput[0] in ["<", ">"]:
            result = self.setContext(contexts_dict[userInput[0]], userInput[1:])
            shouldSwitchToMainContext = (result is  None) or (result[0] != 1) or (result[1] != ":t") #return to main context only if the user hasn't chosen to toggle
        elif userInput in [":n", ":N"]:
            if len(self.prevNavigationFilter) > 0:
                contexts_dictKey = "<<" if userInput == ":n" else ">>"
                result = self.setContext(contexts_dict[contexts_dictKey], self.prevNavigationFilter)
                shouldSwitchToMainContext = (result is  None) or (result[0] != 1) or (result[1] != ":t") #return to main context only if the user hasn't chosen to toggle
            else:
                print("No navigation filter previously entered.")
        elif len(userInput) >= 2 and userInput[0:2] in [":<", "::"]:
            result = self.setContext(contexts_dict[userInput[0:2]], userInput[2:])
            shouldSwitchToMainContext = (result is  None) or (result[0] != 1) or (result[1] != ":t") #return to main context only if the user hasn't chosen to toggle
        elif userInput in [":f", ":F"]:
            if len(self.prevCommandsFilter) > 0:
                contexts_dictKey = ":<" if userInput == ":f" else "::"
                result = self.setContext(contexts_dict[contexts_dictKey], self.prevCommandsFilter)
                shouldSwitchToMainContext = (result is  None) or (result[0] != 1) or (result[1] != ":t") #return to main context only if the user hasn't chosen to toggle
            else:
                print("No commands filter previously entered.")
        elif userInput == ":t":
            newContext = context_switch_dict[self.currentContext]
            if len(newContext) > 0:
                result = self.setContext(newContext, self.currentFilter)
                shouldSwitchToMainContext = (result is  None) or (result[0] != 1) or (result[1] != ":t") #return to main context only if the user hasn't chosen to toggle
            else:
                print("Unable to toggle, not in the right menu!")
        elif userInput == ",":
            result = nav.goTo(self.prevDir, os.getcwd(), self.syncWithFinder)
            self.status = 4 if result[0] == 0 else self.status
        elif userInput == ":-":
            if len(self.prevCommand) > 0:
                result = cmd.executeCommandWithStatus(self.prevCommand, True)
                self.status = 2 if result[0] == 0 else self.status # force updating previous command and its finishing status (although command is just repeated); the command might for example finish with errors although when previously executed it finished successfully (e.g. when removing a file and then attempting to remove it again)
            else:
                print("No shell command previously executed")
        elif userInput == ":":
            result = cmd.editAndExecPrevCmd(self.prevCommand) if self.prevCommand != "" else cmd.editAndExecPrevCmd()
            self.status = 2 if result[0] == 0 else self.status
        elif userInput == "+>":
            nav.addDirToFavorites()
        elif userInput == "->":
            result = nav.removeDirFromFavorites()
            self.status = 1 if result[0] == 1 else self.status
        elif userInput in [":clearnavigation", ":clearcommands"]:
            handleClearMenu(userInput)
        elif userInput in [":c", ":m", ":y", ":ec", ":dc"]:
            handleClipboardInput(userInput, self.clipboard)
        elif userInput in [":td", ":M", ":C", ":etd", ":dtd"]:
            handleRecursiveTransferInput(userInput, self.recursiveTransfer)
        elif userInput.startswith(":") and userInput[1:] in renaming_commands:
            rn.rename(renaming_translations[userInput[1:]])
        elif len(userInput) > 1 and userInput[len(userInput)-1] == ":":
            print("Input cancelled, no action performed!")
        elif userInput in ["?", "?clip", "?ren"]:
            handleHelpRequest(userInput, out)
        elif userInput == ":s":
            self.handleSyncWithFinder()
        elif userInput == "!":
            handleCloseApplication(self.prevCommand)
        else:
            if len(userInput) > 0 and userInput[0] == ":":
                result = cmd.executeCommandWithStatus(userInput[1:])
                self.status = 2
            else:
                result = nav.goTo(userInput, self.prevDir, self.syncWithFinder)
                self.status = 4 if result[0] == 0 else self.status
        if result is not None:
            self.passedInput = result[1]
            self.passedOutput = result[2]
        if shouldSwitchToMainContext:
            self.setContext(contexts_dict["main"], "")

    ''' Contexts are related to main menus:
        - navigation history
        - filtered navigation history
        - favorites
        - command history in execute mode (filtered or not)
        - command history in edit mode (filtered or not)
        - main navigation mode (no main menu): includes all sub-contexts: edit an individual command, help menu, move/copy, recursive move/copy, renaming files/dirs etc '''
    def setContext(self, newContext, userInput):
        assert newContext in valid_contexts, "Invalid context detected"
        if len(self.currentFilter) > 0:
            if self.currentContext in ["-fh", "-ff"]:
                self.prevNavigationFilter = self.currentFilter
            elif self.currentContext in ["--execute", "--edit"]:
                self.prevCommandsFilter = self.currentFilter
            else:
                assert False, "Invalid filter keyword within current context"
        self.currentContext = newContext
        self.currentFilter = ""
        result = None  # a valid result should contain: (status code, passed input, passed output)
        if self.currentContext in ["--execute", "--edit"]:
            self.currentFilter = userInput
            result = cmd.visitCommandMenu(self.currentContext, self.currentFilter, self.prevCommand)
            self.status = 2 if result[0] == 0 else 1 if result[0] == 1 else self.status
        elif self.currentContext in ["-f", "-h"]:
            result = nav.executeGoToFromMenu(self.currentContext, self.prevDir, self.syncWithFinder, userInput, self.prevCommand)
            if len(userInput) > 0:
                self.status = 4 if result[0] == 0 else 1 if (result[0] == 1 or result[0] == 4) else self.status #forward user input if history menu is empty and the user enters <[entry_nr] (result == 4)
            else:
                self.status = 4 if result[0] <= 0 else 1 if result[0] == 1 else self.status
                if result[0] == -1:
                    self.recursiveTransfer.setTargetDir(result[1])
        elif self.currentContext in ["-fh", "-ff"]:
            if len(userInput) > 0:
                self.currentFilter = userInput
                result = nav.executeGoToFromMenu(self.currentContext, self.prevDir, self.syncWithFinder, userInput, self.prevCommand)
                self.status = 4 if result[0] <= 0 else 1 if result[0] == 1 else self.status
                if result[0] == -1:
                    self.recursiveTransfer.setTargetDir(result[1])
            else:
                print("No filter keyword entered. Cannot filter ", end='')
                print("navigation history.") if self.currentContext == "-fh" else print("favorites.")
        return result

    def handleSyncWithFinder(self):
        self.syncWithFinder = not self.syncWithFinder
        print("Finder synchronization enabled") if self.syncWithFinder == True else print("Finder synchronization disabled")
        if self.syncWithFinder == True:
            nav.doFinderSync()
        else:
            nav.handleCloseFinderWhenSyncOff()

''' Helper functions '''
def handleHelpRequest(helpInput, out):
    if helpInput == "?":
        out.displayHelp()
    elif helpInput == "?clip":
        out.displayClipboardHelp()
    elif helpInput == "?ren":
        out.displayRenamingHelp()
    else:
        assert False, "Invalid help option"

def handleClipboardInput(clipboardInput, clipboard):
    if clipboardInput == ":c":
        clipboard.createAction()
    elif clipboardInput == ":m":
        clipboard.createAction(False)
    elif clipboardInput == ":y":
        clipboard.applyAction()
    elif clipboardInput == ":ec":
        clipboard.erase(True)
    elif clipboardInput == ":dc":
        clipboard.display()
    else:
        assert False, "Invalid clipboard option"

def handleRecursiveTransferInput(recursiveTransferInput, recursiveTransfer):
    if recursiveTransferInput == ":td":
        recursiveTransfer.setTargetDir()
    elif recursiveTransferInput == ":M":
        recursiveTransfer.transferItemsToTargetDir(False)
    elif recursiveTransferInput == ":C":
        recursiveTransfer.transferItemsToTargetDir()
    elif recursiveTransferInput == ":etd":
        recursiveTransfer.eraseTargetDir(True)
    elif recursiveTransferInput == ":dtd":
        recursiveTransfer.displayTargetDir()
    else:
        assert False, "Invalid recursive transfer option"

def handleClearMenu(userInput):
    if userInput == ":clearnavigation":
        nav.clearVisitedDirsMenu()
    elif userInput == ":clearcommands":
        cmd.clearCommandHistory()
    else:
        assert False, "Invalid clear menu option"

def handleCloseApplication(previousCommand):
    print("You exited the navigation app.")
    print("")
    print("Last visited directory: " + os.getcwd())
    print("Last executed shell command: ", end='')
    print(previousCommand) if len(previousCommand) > 0 else print("none")
    print("")

application = Application()
application.execute()
