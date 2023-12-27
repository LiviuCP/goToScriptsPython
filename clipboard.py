import os, system_functionality as sysfunc, display as out
from os.path import expanduser, isdir

class Clipboard:
    def __init__(self):
        self.outPath = expanduser("~") + "/.store_output"
        self.erase()
    def erase(self, displayMessage = False):
        self.action = ""
        self.keyword = ""
        self.sourceDir = ""
        if displayMessage == True:
            print("Clipboard erased!")
    def createAction(self, copy = True):
        syncResult = sysfunc.syncCurrentDir()
        assert not syncResult[1], "Current directory fallback not allowed, should have already been performed!"
        status = 0 #default status, successful execution
        self.action = "cp -irv" if copy == True else "mv -iv"
        actionLabel = "copy" if copy == True else "move"
        print("1. Current directory:")
        print(syncResult[0])
        print()
        print("2. Items contained (hidden ones are excluded):")
        print()
        out.displayDirContent(syncResult[0])
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
            self.sourceDir = syncResult[0]
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
        syncResult = sysfunc.syncCurrentDir()
        assert not syncResult[1], "Current directory fallback not allowed"
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
            print("NO") if self.sourceDir == syncResult[0] else print("YES")
    def applyAction(self):
        syncResult = sysfunc.syncCurrentDir()
        assert not syncResult[1], "Current directory fallback not allowed"
        if len(self.action) == 0:
            print("Error! The clipboard is empty.")
            status = 1
        else:
            actionLabel = "move" if self.action == "mv -iv" else "copy"
            destDir = syncResult[0]
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
                clipboardCommandStatus = "status=$?;" + "\n"
                writeStatusToFile = "echo $status > " + self.outPath + ";" + "\n"
                command = cdCommand + clipboardCommand + clipboardCommandStatus + writeStatusToFile
                print(f"Started the {actionLabel} operation.")
                print()
                os.system(command)
                status = 4 # error/exception during execution of move/copy command
                with open(self.outPath, "r") as outputStorage:
                    executionStatus = outputStorage.readline().strip("\n")
                    print()
                    if executionStatus == "0":
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
