import os, subprocess
from system import system_functionality as sysfunc
from utilities import display as out

class Clipboard:
    def __init__(self):
        self.erase()
    def erase(self, displayMessage = False):
        self.action = ""
        self.keyword = ""
        self.sourceDir = ""
        if displayMessage == True:
            print("Clipboard erased!")
    def createAction(self, copy = True):
        syncedCurrentDir, fallbackPerformed = sysfunc.syncCurrentDir()
        assert not fallbackPerformed, "Current directory fallback not allowed, should have already been performed!"
        status = 0 #default status, successful execution
        self.action = "cp -irv" if copy == True else "mv -iv"
        actionLabel = "copy" if copy == True else "move"
        print("1. Current directory:")
        print(syncedCurrentDir)
        print()
        print("2. Items contained (hidden ones are excluded):")
        print()
        out.displayDirContent(syncedCurrentDir)
        print()
        print("3. Clipboard action: ", end='')
        print(actionLabel)
        print()
        keyInterruptOccurred = False
        try:
            self.keyword = input("Enter keyword: ")
        except (KeyboardInterrupt, EOFError):
            keyInterruptOccurred = True
        os.system("clear")
        if len(self.keyword) > 0 and not keyInterruptOccurred:
            self.sourceDir = syncedCurrentDir
            print(f"The {actionLabel} command has been successfully built.")
            print(f"Keyword: {self.keyword}")
            print("Please choose the destination directory and paste when ready.")
        else:
            self.erase()
            status = 1
            if keyInterruptOccurred:
                print("Operation aborted by user. Clipboard erased.")
            else:
                print("No keyword input. Clipboard erased.")
                print("Please try again.")
        return status
    def display(self):
        syncedCurrentDir, fallbackPerformed = sysfunc.syncCurrentDir()
        assert not fallbackPerformed, "Current directory fallback not allowed"
        if len(self.action) == 0:
            print("The clipboard is empty!")
        elif not os.path.isdir(self.sourceDir):
            print("The source directory contained in clipboard is invalid.")
            print("It might have been deleted, renamed or moved.")
            print("Directory path: " + self.sourceDir)
        else:
            print("The clipboard has following status: ")
            print()
            print(f"Action: {self.action}")
            print(f"Source directory: {self.sourceDir}")
            print(f"Keyword: {self.keyword}")
            print("Can apply to current directory: ", end='')
            print("NO") if self.sourceDir == syncedCurrentDir else print("YES")
    def applyAction(self):
        syncedCurrentDir, fallbackPerformed = sysfunc.syncCurrentDir()
        assert not fallbackPerformed, "Current directory fallback not allowed"
        if len(self.action) == 0:
            print("Error! The clipboard is empty.")
            status = 1
        else:
            actionLabel = "move" if self.action == "mv -iv" else "copy"
            destDir = syncedCurrentDir
            if not os.path.isdir(self.sourceDir):
                print("The source directory contained in clipboard is invalid.")
                print("It might have been deleted, renamed or moved.")
                print(f"Directory path: {self.sourceDir}")
                status = 2
            elif self.sourceDir == destDir:
                print(f"Cannot {actionLabel}. Source and destination directory are the same.")
                status = 3
            else:
                cdCommand = "cd " + self.sourceDir + ";" + "\n"
                clipboardCommand = self.action + " " + self.keyword + ' \"' + destDir + '\";' + "\n"
                command = cdCommand + clipboardCommand
                print(f"Started the {actionLabel} operation.")
                print()
                result = subprocess.run(command, shell=True)
                executionStatus = result.returncode
                status = 4 # error/exception during execution of move/copy command
                print()
                if executionStatus == 0:
                    status = 0 # success
                    print(f"Finished the {actionLabel} operation")
                else:
                    print(f"The {actionLabel} operation finished with errors.")
                    print("Please check the source and destination directories.")
                if actionLabel == "move":
                    print("For a new operation please add items to clipboard.")
                elif status == 0:
                    print("The copy operation can be repeated in the same or in a different directory.")
                    print("Clipboard NOT erased.")
        if status in [2, 4] or (status != 3 and self.action == "mv -iv"):
            self.erase(True)
        return status
    def getActionLabel(self):
        return "move" if self.action.startswith("mv") else "copy" if self.action.startswith("cp") else ""
    def getKeyword(self):
        return self.keyword
    def getSourceDir(self):
        return self.sourceDir
