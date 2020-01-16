import os, display as out
from os.path import expanduser, isdir

home_dir = expanduser("~") + "/"
clipboard_storage_file = home_dir + ".store_clipboard"
output_storage_file = home_dir + ".store_output"

def add(copy = True):
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

def applyData():
    with open(clipboard_storage_file, "r") as clipboardStorage:
        status = 0 # default status, normal execution
        clipboardContent = clipboardStorage.readlines()
        if len(clipboardContent) < 3:
            print("Error! Incomplete or empty clipboard.")
            status = 1
        else:
            operation = clipboardContent[0].strip("\n")
            sourceDir = clipboardContent[1].strip("\n")
            destDir = os.getcwd()
            keyword = clipboardContent[2].strip("\n")
            action = "move" if operation == "mv -iv" else "copy" if operation == "cp -irv" else ""
            clipboardStorage.close()
            if action == "":
                with open(clipboard_storage_file, "w") as clipboardStorage:
                    status = 2
                    print("Error! The clipboard is corrupt, no valid action contained.")
                    print("Clipboard erased.")
            elif not os.path.isdir(sourceDir):
                with open(clipboard_storage_file, "w") as clipboardStorage:
                    status = 3
                    print("Invalid source directory: " + sourceDir)
                    print("It might have been deleted, renamed or moved.")
                    print("Clipboard erased.")
            elif keyword == "":
                with open(clipboard_storage_file, "w") as clipboardStorage:
                    status = 4
                    print("Error! No keyword found.")
                    print("Clipboard erased.")
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
                    if action == "move":
                        with open(clipboard_storage_file, "w") as clipboardStorage:
                            print("Clipboard erased.")
                            print("For a new operation please add items to clipboard.")
                    else:
                        print("The copy operation can be repeated in the same or in a different directory.")
                        print("Clipboard NOT erased.")
        return status
