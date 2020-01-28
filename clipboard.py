import os, display as out
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
        status = 0 #default status, successful execution
        self.action = "cp -irv" if copy == True else "mv -iv"
        actionLabel = "copy" if copy == True else "move"
        print("1. Current directory:")
        print(os.getcwd())
        print()
        print("2. Items contained (hidden ones are excluded):")
        print()
        out.displayCurrentDirContent()
        print()
        print("3. Clipboard action: ", end='')
        print(actionLabel)
        print()
        self.keyword = input("Enter keyword: ")
        os.system("clear")
        if self.keyword == "":
            self.erase()
            print("No keyword input. Clipboard erased.")
            print("Please try again.")
            status = 1
        else:
            self.sourceDir = os.getcwd()
            print("The " + actionLabel + " command has been successfully built.")
            print("Keyword: " + self.keyword)
            print("Please choose the destination directory and paste when ready.")
        return status
    def display(self):
        if self.action == "":
            print("The clipboard is empty!")
        elif not os.path.isdir(self.sourceDir):
            print("The source directory contained in clipboard is invalid.")
            print("It might have been deleted, renamed or moved.")
            print("Directory path: " + self.sourceDir)
        else:
            print("The clipboard has following status: ")
            print()
            print("Action: " + self.action)
            print("Source directory: " + self.sourceDir)
            print("Keyword: " + self.keyword)
            print("Can apply to current directory: ", end='')
            print("NO") if self.sourceDir == os.getcwd() else print("YES")
    def applyAction(self):
        if self.action == "":
            print("Error! The clipboard is empty.")
            status = 1
        else:
            actionLabel = "move" if self.action == "mv -iv" else "copy"
            destDir = os.getcwd()
            if not os.path.isdir(self.sourceDir):
                print("The source directory contained in clipboard is invalid.")
                print("It might have been deleted, renamed or moved.")
                print("Directory path: " + self.sourceDir)
                status = 2
            elif self.sourceDir == destDir:
                print("Cannot " + actionLabel + ". Source and destination directory are the same.")
                status = 3
            else:
                cdCommand = "cd " + self.sourceDir + ";" + "\n"
                clipboardCommand = self.action + " " + self.keyword + ' \"' + destDir + '\";' + "\n"
                clipboardCommandStatus = "status=$?;" + "\n"
                writeStatusToFile = "echo $status > " + self.outPath + ";" + "\n"
                command = cdCommand + clipboardCommand + clipboardCommandStatus + writeStatusToFile
                print("Started the " + actionLabel + " operation.")
                print()
                os.system(command)
                status = 4 # error/exception during execution of move/copy command
                with open(self.outPath, "r") as outputStorage:
                    executionStatus = outputStorage.readline().strip("\n")
                    print()
                    if executionStatus == "0":
                        status = 0 # success
                        print("Finished the " + actionLabel + " operation")
                    else:
                        print("The " + actionLabel + " operation finished with errors.")
                        print("Please check the source and destination directories.")
                    if actionLabel == "move":
                        print("For a new operation please add items to clipboard.")
                    elif status == 0:
                        print("The copy operation can be repeated in the same or in a different directory.")
                        print("Clipboard NOT erased.")
        if status in [2, 4] or (status != 3 and self.action == "mv -iv"):
            self.erase(True)
        return status
