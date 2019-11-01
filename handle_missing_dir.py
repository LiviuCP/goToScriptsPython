import sys, os
from os.path import expanduser
import remove_missing_dir, map_missing_dir

home_dir = expanduser("~") + "/"
input_storage_file = home_dir + ".store_input"
output_storage_file = home_dir + ".store_output"

# The status returned by this method is stored into the .store_output file to be picked by the BASH script
# It can have following values:
# :0 - mapping or removal attempted by user
# :1 - user input stored in .store_input, to be picked and forwarded by BASH
# :2 - user exited the choose path dialog, no further actions
# :3 - invalid or missing arguments
# :4 - only used by current method (replacing directory does not exist)
def handleMissingDir():
    # we need two arguments, one for missing directory path and second for menu type (history/favorites)
    if len(sys.argv) < 3:
        print("handle_missing_dir.py: missing arguments")
        outcome = ":3"
    elif sys.argv[2] != '-h' and sys.argv[2] != '-f':
        print("handle_missing_dir.py: invalid second argument")
        outcome = ":3"
    else:
        missingDirPath = sys.argv[1]
        menuType = "history" if sys.argv[2] == '-h' else "favorites"

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
            remove_missing_dir.removeDir(missingDirPath)
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
                replacingDirPath = output_storage.readline()
            if replacingDirPath == ":4":
                print("")
                print("The chosen replacing directory (" + replacingDir + ") does not exist or has been deleted")
                print("")
                print("Mapping failed.")
            else:
                print ("Replacing dir absolute path is: " + replacingDirPath)
                map_missing_dir.replaceDir(missingDirPath, replacingDirPath)
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

        with open(output_storage_file, "w") as output_storage:
            output_storage.write(outcome)

handleMissingDir()
