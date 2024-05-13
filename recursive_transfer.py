import os, common, system_functionality as sysfunc, display as out

class RecursiveTransfer:
    def __init__(self):
        self.eraseTargetDir()
    def eraseTargetDir(self, displayMessage = False):
        self.targetDir = ""
        if displayMessage == True:
            print("The target directory has been erased.")
    def displayTargetDir(self):
        syncedCurrentDir, fallbackPerformed = sysfunc.syncCurrentDir()
        assert not fallbackPerformed, "Current directory fallback not allowed"
        if len(self.targetDir) == 0:
            print("No target directory has been setup.")
        elif not os.path.isdir(self.targetDir):
            print(f"Invalid target directory: {self.targetDir}")
            print("Please setup a valid target directory!")
        else:
            print(f"The target directory path for recursive move/copy is: {self.targetDir}")
            print("Can start transfer operations from current dir: ", end='')
            print("NO") if self.targetDir == syncedCurrentDir else print("YES")
    def setTargetDir(self, directory = ""):
        syncedCurrentDir, fallbackPerformed = sysfunc.syncCurrentDir()
        assert not fallbackPerformed, "Current directory fallback not allowed"
        isValidDir = False
        if len(directory) == 0:
            self.targetDir = syncedCurrentDir
            isValidDir = True
        else:
            targetDir = common.getAbsoluteDirPath(directory)
            if len(targetDir) > 0:
                self.targetDir = targetDir
                isValidDir = True
        if isValidDir:
            print("Set new target directory for recursive moving/copying.")
            print(f"Target path: {self.targetDir}")
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
        syncedCurrentDir, fallbackPerformed = sysfunc.syncCurrentDir()
        assert not fallbackPerformed, "Current directory fallback not allowed, should have already been performed!"
        actionLabel = "copy" if copy == True else "move"
        if len(self.targetDir) == 0:
            print("No target directory has been setup.")
        elif not os.path.isdir(self.targetDir):
            print(f"Invalid target directory: {self.targetDir}")
            print("Please setup a valid target directory!")
        elif self.targetDir == syncedCurrentDir:
            print("The source and target directory are the same.")
            print(f"Cannot enter recursive {actionLabel} mode.")
        else:
            os.system("clear")
            print(f"Entered recursive {actionLabel} mode")
            print()
            print("*********************************************************************************************************************************************************")
            print()
            action = "mv -iv" if actionLabel == "move" else "cp -irv"
            keyword = ""
            while True:
                print("1. Current directory:")
                print(syncedCurrentDir)
                print()
                print("2. Items contained (hidden ones are excluded):")
                print()
                out.displayDirContent(syncedCurrentDir)
                print()
                print("3. Recursive clipboard operation: ", end='')
                print(actionLabel)
                print()
                print(f"4. Destination directory: {self.targetDir}")
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
                syncedCurrentDir, fallbackPerformed = sysfunc.syncCurrentDir() # handle the situation when current dir becomes inaccessible during recursive transferring process
                if fallbackPerformed:
                    out.printFallbackMessage("Recursive " + actionLabel + " mode aborted!")
                elif not os.path.isdir(self.targetDir):
                    print(f"Recursive {actionLabel} mode aborted!")
                    print(f"Invalid target directory (probably deleted): {self.targetDir}")
                elif len(keyword) == 0 or keyInterruptOccurred:
                    print(f"Exited recursive {actionLabel} mode")
                else:
                    command = action + " " + keyword + ' \"' + self.targetDir + '\";'
                    os.system(command)
                    print()
                    print("*********************************************************************************************************************************************************")
                    print()
                    continue
                break
