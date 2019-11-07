import sys, os
from os.path import expanduser
import consolidate_history1 as consolidate_hist
import update_individual_history_files as update_hist

home_dir = expanduser("~") + "/"
input_storage_file = home_dir + ".store_input"
output_storage_file = home_dir + ".store_output"

def goTo():
    prevDir = os.getcwd()

    if len(sys.argv) == 1:
        directory = home_dir
    else:
        directory = sys.argv[1]

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
            update_hist.update(currentDir)
            consolidate_hist.consolidate()
    else:
        # in this phase the calling BASH script will take over the current directory name from input file no matter if cd has been successful or not
        with open(input_storage_file, "w") as input_storage:
            input_storage.write(prevDir)
        # use the prev dir provided by BASH in case of error (so the previously visited dir remains the same)
        #if len(sys.argv) >= 3:
        prevDir = sys.argv[2]
        print("Error when attempting to change directory! Possible causes: ")
        print(" - chosen directory path does not exist")
        print(" - chosen path is not a directory")
        print(" - insufficient access rights")
        print("Please try again!")

    # used by BASH to determine the previous directory
    with open(output_storage_file, "w") as output_storage:
        output_storage.write(prevDir)

goTo()
