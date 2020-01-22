import os, display as out
from os.path import expanduser, isdir

home_dir = expanduser("~") + "/"
clipboard_storage_file = home_dir + ".store_clipboard"
input_storage_file = home_dir + ".store_input"
output_storage_file = home_dir + ".store_output"
target_dir_file = home_dir + ".store_target_dir"

def createAction(copy = True):
    status = 0 #default status, successful execution
    operation = "cp -irv" if copy == True else "mv -iv"
    operationLabel = "copy" if copy == True else "move"
    print("1. Current directory:")
    print(os.getcwd())
    print()
    print("2. Items contained (hidden ones are excluded):")
    print()
    out.displayCurrentDirContent()
    print()
    print("3. Clipboard operation: ", end='')
    print(operationLabel)
    print()
    keyword = input("Enter keyword: ")
    os.system("clear")
    with open(clipboard_storage_file, "w") as clipboardStorage:
        if keyword == "":
            print("No input. Clipboard erased.")
            print("Please try again.")
            status = 1
        else:
            clipboardStorage.write(operation + "\n")
            clipboardStorage.write(os.getcwd() + "\n")
            clipboardStorage.write(keyword + "\n")
            print("The " + operationLabel + " command has been successfully built.")
            print("Keyword: " + keyword)
            print("Please choose the destination directory and paste when ready.")
    return status

def applyAction():
    with open(clipboard_storage_file, "r") as clipboardStorage:
        status = 0 # default status, normal execution
        clipboardContent = clipboardStorage.readlines()
        clipboardStorage.close()
        if len(clipboardContent) < 3:
            print("Error! Incomplete or empty clipboard.")
            status = 1
        else:
            operation = clipboardContent[0].strip("\n")
            sourceDir = clipboardContent[1].strip("\n")
            destDir = os.getcwd()
            keyword = clipboardContent[2].strip("\n")
            action = "move" if operation == "mv -iv" else "copy" if operation == "cp -irv" else ""
            if action == "":
                status = 2
                print("Error! The clipboard is corrupt, no valid action contained.")
            elif not os.path.isdir(sourceDir):
                status = 3
                print("The source directory contained in clipboard is invalid.")
                print("It might have been deleted, renamed or moved.")
                print("Directory path: " + sourceDir)
            elif keyword == "":
                status = 4
                print("Error! No keyword found in clipboard.")
            elif sourceDir == destDir:
                print("Cannot " + action + ". Source and destination directory are the same.")
                status = 5
            else:
                cdCommand = "cd " + sourceDir + ";" + "\n"
                clipboardCommand = operation + " " + keyword + ' \"' + destDir + '\";' + "\n"
                clipboardCommandStatus = "status=$?;" + "\n"
                writeStatusToFile = "echo $status > " + output_storage_file + ";" + "\n"
                command = cdCommand + clipboardCommand + clipboardCommandStatus + writeStatusToFile
                print("Started the " + action + " operation.")
                print()
                os.system(command)
                with open(output_storage_file, "r") as outputStorage:
                    executionStatus = outputStorage.readline().strip("\n")
                    print()
                    if executionStatus == "0":
                        print("Finished the " + action + " operation")
                    else:
                        print("The " + action + " operation finished with errors or user chose to override only part of the content.")
                        print("Please check the source and destination directories.")
                        status = 6
                    if action == "move":
                        print("For a new operation please add items to clipboard.")
                    elif status == 0:
                        print("The copy operation can be repeated in the same or in a different directory.")
                        print("Clipboard NOT erased.")
        if status in [1, 2, 3, 4, 6] or action == "move":
            erase()
        return status

def erase():
    with open(clipboard_storage_file, "w") as clipboardStorage:
        print("Clipboard erased.")

def display():
    with open(clipboard_storage_file, "r") as clipboardStorage:
        clipboardContent = clipboardStorage.readlines()
        if len(clipboardContent) == 0:
            print("The clipboard is empty!")
        elif len(clipboardContent) < 3:
            print("The clipboard is corrupt. Please erase it or initiate a new move/copy operation.")
        else:
            operation = clipboardContent[0].strip("\n")
            sourceDir = clipboardContent[1].strip("\n")
            keyword = clipboardContent[2].strip("\n")
            action = "move" if operation == "mv -iv" else "copy" if operation == "cp -irv" else ""
            if action == "":
                print("Error! The clipboard is corrupt, no valid action contained.")
            elif not os.path.isdir(sourceDir):
                print("The source directory contained in clipboard is invalid.")
                print("It might have been deleted, renamed or moved.")
                print("Directory path: " + sourceDir)
            elif keyword == "":
                print("Error! No keyword found in clipboard.")
            else:
                print("The clipboard has following status: ")
                print()
                print("Action: " + action)
                print("Source directory: " + sourceDir)
                print("Keyword: " + keyword)
                print("Can apply to current directory: ", end='')
                print("NO") if sourceDir == os.getcwd() else print("YES")

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
