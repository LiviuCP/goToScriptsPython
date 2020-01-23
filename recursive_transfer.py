import os, display as out
from os.path import expanduser, isdir

home_dir = expanduser("~") + "/"
input_storage_file = home_dir + ".store_input"
output_storage_file = home_dir + ".store_output"
target_dir_file = home_dir + ".store_target_dir"

def setTargetDir(directory = ""):
    isValidDir = False
    if directory == "":
        targetDir = os.getcwd()
        isValidDir = True
    else:
        # build and execute command
        getDir = "directory=`echo " + directory + "`;" #if wildcards are being used the full dir name should be expanded
        cdCommand = "cd " + '\"' + "$directory" + '\"' + " 2> /dev/null;"
        executionStatus = "echo $? > " + output_storage_file + ";"
        writeCurrentDir = "pwd > " + input_storage_file + ";"
        executeCommandWithStatus = getDir + "\n" + cdCommand + "\n" + executionStatus + "\n" + writeCurrentDir
        os.system(executeCommandWithStatus)
        # read command exit code and create the status message
        with open(output_storage_file, "r") as outputStorage:
            if outputStorage.readline().strip('\n') == "0":
                with open(input_storage_file, "r") as inputStorage:
                    targetDir = inputStorage.readline().strip('\n')
                    isValidDir = True
    if isValidDir == True:
        with open(target_dir_file, "w") as target:
            target.write(targetDir)
            print("Set new target directory for recursive moving/copying.")
            print("Target path: " + targetDir)
    else:
        print("Error when attempting to setup target directory! Possible causes: ")
        print(" - chosen directory path does not exist or has been deleted")
        print(" - chosen path is not a directory")
        print(" - insufficient access rights")
        print(" - other error")
        print("Please try again!")

def transferItemsToTargetDir(copy = True):
    with open(target_dir_file, "r") as target:
        action = "copy" if copy == True else "move"
        targetDir = target.readline().strip("\n")
        if targetDir == "":
            print("No target directory has been setup.")
        elif not os.path.isdir(targetDir):
            print("Invalid target directory: " + targetDir)
            print("Please setup a valid target directory!")
        elif targetDir == os.getcwd():
            print("The source and target directory are the same.")
            print("Cannot enter recursive " + action + " mode.")
        else:
            os.system("clear")
            print("Recursive " + action + " mode enabled")
            print()
            print("*********************************************************************************************************************************************************")
            print()
            transferOperation = "mv -iv" if action == "move" else "cp -irv"
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
                print(action)
                print()
                print("4. Destination directory: " + targetDir)
                print()
                print("5. Previously used keyword: ", end='')
                print(keyword) if keyword != "" else print("none")
                print()
                keyword = input("Enter keyword: ")
                os.system("clear")
                if keyword == "":
                    print("Recursive " + action + " mode disabled")
                    break
                else:
                    command = transferOperation + " " + keyword + ' \"' + targetDir + '\";'
                    os.system(command)
                    print()
                    print("*********************************************************************************************************************************************************")
                    print()

def eraseTargetDir():
    with open(target_dir_file, "w") as target:
        print("The target directory has been erased.")

def displayTargetDir():
    with open(target_dir_file, "r") as target:
        targetDir = target.readline().strip("\n")
        if targetDir == "":
            print("No target directory has been setup.")
        elif not os.path.isdir(targetDir):
            print("Invalid target directory: " + targetDir)
            print("Please setup a valid target directory!")
        else:
            print("The target directory path for recursive move/copy is: " + targetDir)
