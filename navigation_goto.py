import sys, os
import nav_menus_update as nav
from os.path import expanduser, isdir

home_dir = expanduser("~") + "/"
input_storage_file = home_dir + ".store_input"
output_storage_file = home_dir + ".store_output"

# 1) Visit navigation menu

def visitNavigationMenu(menuChoice = "", previousDir = "", userInput = ""):
    status = 0 # default status, normal execution or missing dir successful removal/mapping
    if menuChoice == "" or previousDir == "":
        print("Insufficient number of arguments")
        status = 3
    elif userInput == "":
        prevDir = previousDir
        dirPath = nav.choosePath(menuChoice)
    else:
        prevDir = previousDir
        dirPath = nav.choosePath(menuChoice, userInput)
    if dirPath == ":1" or dirPath == ":2" or dirPath == ":4":
        status = int(dirPath[1])
    elif dirPath != ":3":
        if not os.path.isdir(dirPath):
            result = handleMissingDir(dirPath, menuChoice)
            if result == ":1":
                status = 1 #forward user input
        else:
            goTo(dirPath, prevDir)
    else:
        status = 3
    return status

# 2) Go to directory
def goTo(gt_directory = "", prev_directory = ""):
    prevDir = os.getcwd()

    if gt_directory == "":
        directory = home_dir
    else:
        directory = gt_directory

    # build and execute command
    getDir = "directory=`echo " + directory + "`;" #if wildcards are being used the full dir name should be expanded
    sourceCommand = "source ~/.bashrc;" #include .bashrc to ensure the aliases and scripts work
    executionStatus = "echo $? > " + output_storage_file + ";"
    cdCommand = "cd " + '\"' + "$directory" + '\"' + " 2> /dev/null;"
    writeCurrentDir = "pwd > " + input_storage_file + ";"
    executeCommandWithStatus = getDir + "\n" + sourceCommand + "\n" + cdCommand + "\n" + executionStatus + "\n" + writeCurrentDir
    os.system(executeCommandWithStatus)

    # read command exit code and create the status message
    with open(output_storage_file, "r") as output_storage:
        success = True if output_storage.readline().strip('\n') == "0" else False
    if success == True:
        with open(input_storage_file, "r") as input_storage:
            currentDir = input_storage.readline().strip('\n')
        os.chdir(currentDir)
        print("Previous directory: " + prevDir)
        print("Current directory: " + currentDir)
        if (prevDir != currentDir):
            nav.updateHistory(currentDir)
            nav.consolidateHistory()
    else:
        # in this phase the calling BASH script will take over the current directory name from input file no matter if cd has been successful or not
        with open(input_storage_file, "w") as input_storage:
            input_storage.write(prevDir)
        # use the prev dir provided by BASH in case of error (so the previously visited dir remains the same)
        prevDir = prev_directory
        print("Error when attempting to change directory! Possible causes: ")
        print(" - chosen directory path does not exist or has been deleted")
        print(" - chosen path is not a directory")
        print(" - insufficient access rights")
        print("Please try again!")

    # used by BASH to determine the previous directory
    with open(output_storage_file, "w") as output_storage:
        output_storage.write(prevDir)

# 3) Handle missing directory in navigation menu

# The status returned by this method is stored into the .store_output file to be picked by the BASH script
# It can have following values:
# :0 - mapping or removal attempted by user
# :1 - user input stored in .store_input, to be picked and forwarded by BASH
# :2 - user exited the choose path dialog, no further actions
# :3 - invalid or missing arguments
# :4 - only used by current method (replacing directory does not exist)
def handleMissingDir(path, menu):
    # we need two arguments, one for missing directory path and second for menu type (history/favorites)
    if path == "" or menu == "":
        print("handleMissingDir: missing arguments")
        outcome = ":3"
    elif menu != '-h' and menu != '-f':
        print("handleMissingDir: invalid second argument")
        outcome = ":3"
    else:
        missingDirPath = path
        menuType = "history" if menu == '-h' else "favorites"

        os.system("clear")
        print("Invalid path " + missingDirPath)
        print("The directory might have been moved, renamed or deleted.")
        print("")
        print("Please choose the required action: ")
        print("!r to remove the directory from the menus")
        print("!m to map to an existing directory")
        print("! to quit")
        print("")

        userChoice = input()

        # remove directory from history, don't map to anything
        if userChoice == "!r":
            nav.removeMissingDir(missingDirPath)
            outcome = ":0"
        # map missing directory to a valid replacing dir
        elif userChoice == "!m":
            os.system("clear")
            print("Missing directory: " + missingDirPath)
            print("")
            print("Enter the name and/or path of the replacing directory.")
            replacingDir = input()

            with open(input_storage_file, "w") as input_storage:
                input_storage.write(replacingDir)

            # build BASH command for retrieving the absolute path of the replacing dir (if exists)
            command = "input=`head -1 " + input_storage_file + "`; "
            command = command + "output=" + output_storage_file + "; "
            command = command + "cd $input 2> /dev/null; if [[ $? == 0  ]]; then pwd > \"$output\"; else echo :4 > \"$output\"; fi"

            os.system(command)

            with open(output_storage_file, "r") as output_storage:
                replacingDirPath = output_storage.readline().strip('\n')
            if replacingDirPath == ":4":
                os.system("clear")
                print("The chosen replacing directory (" + replacingDir + ") does not exist, has been deleted or you might not have the required access level.")

                print("Cannot perform mapping.")
            else:
                nav.mapMissingDir(missingDirPath, replacingDirPath)
            outcome = ":0"
        elif userChoice == "!":
            os.system("clear")
            print("You exited the " + menuType +  " menu")
            outcome = ":2"
        else:
            # input to be forwarded for further handling to BASH
            with open(input_storage_file, "w") as input_storage:
                input_storage.write(userChoice)
            outcome = ":1"

    return outcome
