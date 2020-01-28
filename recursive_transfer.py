import os, display as out
from os.path import expanduser, isdir

home_dir = expanduser("~") + "/"

class RecursiveTransfer:
    def __init__(self):
        self.inPath = home_dir + ".store_input"
        self.outPath = home_dir + ".store_output"
        self.eraseTargetDir()
    def eraseTargetDir(self, displayMessage = False):
        self.targetDir = ""
        if displayMessage == True:
            print("The target directory has been erased.")
    def displayTargetDir(self):
        if self.targetDir == "":
            print("No target directory has been setup.")
        elif not os.path.isdir(self.targetDir):
            print("Invalid target directory: " + self.targetDir)
            print("Please setup a valid target directory!")
        else:
            print("The target directory path for recursive move/copy is: " + self.targetDir)
            print("Can start transfer operations from current dir: ", end='')
            print("NO") if self.targetDir == os.getcwd() else print("YES")
    def setTargetDir(self, directory = ""):
        isValidDir = False
        if directory == "":
            self.targetDir = os.getcwd()
            isValidDir = True
        else:
            # build and execute command
            getDir = "directory=`echo " + directory + "`;" #if wildcards are being used the full dir name should be expanded
            cdCommand = "cd " + '\"' + "$directory" + '\"' + " 2> /dev/null;"
            executionStatus = "echo $? > " + self.outPath + ";"
            writeCurrentDir = "pwd > " + self.inPath + ";"
            executeCommandWithStatus = getDir + "\n" + cdCommand + "\n" + executionStatus + "\n" + writeCurrentDir
            os.system(executeCommandWithStatus)
            # read command exit code and create the status message
            with open(outPath, "r") as outputStorage:
                if outputStorage.readline().strip('\n') == "0":
                    with open(inPath, "r") as inputStorage:
                        self.targetDir = inputStorage.readline().strip('\n')
                        isValidDir = True
        if isValidDir == True:
            print("Set new target directory for recursive moving/copying.")
            print("Target path: " + self.targetDir)
        else:
            print("Error when attempting to setup target directory! Possible causes: ")
            print(" - chosen directory path does not exist or has been deleted")
            print(" - chosen path is not a directory")
            print(" - insufficient access rights")
            print(" - other error")
            print("Please try again!")
            print()
            self.eraseTargetDir(True)
    def transferItemsToTargetDir(self, copy = True):
        actionLabel = "copy" if copy == True else "move"
        if self.targetDir == "":
            print("No target directory has been setup.")
        elif not os.path.isdir(self.targetDir):
            print("Invalid target directory: " + self.targetDir)
            print("Please setup a valid target directory!")
        elif self.targetDir == os.getcwd():
            print("The source and target directory are the same.")
            print("Cannot enter recursive " + actionLabel + " mode.")
        else:
            os.system("clear")
            print("Recursive " + actionLabel + " mode enabled")
            print()
            print("*********************************************************************************************************************************************************")
            print()
            action = "mv -iv" if actionLabel == "move" else "cp -irv"
            keyword = ""
            while True == True:
                print("1. Current directory:")
                print(os.getcwd())
                print()
                print("2. Items contained (hidden ones are excluded):")
                print()
                out.displayCurrentDirContent()
                print()
                print("3. Recursive clipboard operation: ", end='')
                print(actionLabel)
                print()
                print("4. Destination directory: " + self.targetDir)
                print()
                print("5. Previously used keyword: ", end='')
                print(keyword) if keyword != "" else print("none")
                print()
                keyword = input("Enter keyword: ")
                os.system("clear")
                if keyword == "":
                    print("Recursive " + actionLabel + " mode disabled")
                    break
                else:
                    command = action + " " + keyword + ' \"' + self.targetDir + '\";'
                    os.system(command)
                    print()
                    print("*********************************************************************************************************************************************************")
                    print()
