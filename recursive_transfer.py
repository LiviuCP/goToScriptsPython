import os, system_functionality as sysfunc, display as out
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
        syncResult = sysfunc.syncCurrentDir()
        assert not syncResult[1], "Current directory fallback not allowed"
        if len(self.targetDir) == 0:
            print("No target directory has been setup.")
        elif not os.path.isdir(self.targetDir):
            print("Invalid target directory: " + self.targetDir)
            print("Please setup a valid target directory!")
        else:
            print("The target directory path for recursive move/copy is: " + self.targetDir)
            print("Can start transfer operations from current dir: ", end='')
            print("NO") if self.targetDir == syncResult[0] else print("YES")
    def setTargetDir(self, directory = ""):
        syncResult = sysfunc.syncCurrentDir()
        assert not syncResult[1], "Current directory fallback not allowed"
        isValidDir = False
        if len(directory) == 0:
            self.targetDir = syncResult[0]
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
            with open(self.outPath, "r") as outputStorage:
                if outputStorage.readline().strip('\n') == "0":
                    with open(self.inPath, "r") as inputStorage:
                        self.targetDir = inputStorage.readline().strip('\n')
                        isValidDir = True
        if isValidDir:
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
    def getTargetDir(self):
        return self.targetDir
    def transferItemsToTargetDir(self, copy = True):
        syncResult = sysfunc.syncCurrentDir()
        assert not syncResult[1], "Current directory fallback not allowed"
        actionLabel = "copy" if copy == True else "move"
        if len(self.targetDir) == 0:
            print("No target directory has been setup.")
        elif not os.path.isdir(self.targetDir):
            print("Invalid target directory: " + self.targetDir)
            print("Please setup a valid target directory!")
        elif self.targetDir == syncResult[0]:
            print("The source and target directory are the same.")
            print("Cannot enter recursive " + actionLabel + " mode.")
        else:
            os.system("clear")
            print("Entered recursive " + actionLabel + " mode")
            print()
            print("*********************************************************************************************************************************************************")
            print()
            action = "mv -iv" if actionLabel == "move" else "cp -irv"
            keyword = ""
            while True:
                print("1. Current directory:")
                print(syncResult[0])
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
                keyInterruptOccurred = False
                try:
                    keyword = input("Enter keyword: ")
                except (KeyboardInterrupt, EOFError):
                    keyInterruptOccurred = True
                os.system("clear")
                syncResult = sysfunc.syncCurrentDir() # handle the situation when current dir becomes inaccessible during recursive transferring process
                if syncResult[1]:
                    out.printFallbackMessage("Recursive " + actionLabel + " mode aborted!")
                elif not os.path.isdir(self.targetDir):
                    print("Recursive " + actionLabel + " mode aborted!")
                    print("Invalid target directory (probably deleted): " + self.targetDir)
                elif len(keyword) == 0 or keyInterruptOccurred:
                    print("Exited recursive " + actionLabel + " mode")
                else:
                    command = action + " " + keyword + ' \"' + self.targetDir + '\";'
                    os.system(command)
                    print()
                    print("*********************************************************************************************************************************************************")
                    print()
                    continue
                break
