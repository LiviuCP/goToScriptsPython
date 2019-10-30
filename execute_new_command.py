import sys, os, datetime
from os.path import expanduser
from consolidate_command_history import consolidate

home_dir = expanduser("~") + "/"
c_r_hist_file = home_dir + ".recent_command_history"
output_storage_file = home_dir + ".store_output"

def executeNew():
    minNrOfCmdChars = 10
    if len(sys.argv) == 1:
        print("No argument provided")
    else:
        commandToExecute = sys.argv[1]
        if len(commandToExecute) >= minNrOfCmdChars:
            updateIndividualCommandHistoryFiles(commandToExecute)
            consolidate()

        print("Command is being executed: " + commandToExecute)
        print("--------------------------")

        # build and execute command
        sourceCommand = "source ~/.bashrc;" #include .bashrc to ensure the aliases and scripts work
        executionStatus = "echo $? > " + output_storage_file
        executeCommandWithStatus = sourceCommand + "\n" + commandToExecute + "\n" + executionStatus
        os.system(executeCommandWithStatus)

        # read command status code and create the status message
        with open(output_storage_file, "r") as output:
            status = output.readline().strip('\n')
            printedStatus = "with errors" if status != "0" else "successfully"

        # status message to be written instead of code so it's used by BASH to indicate how the last executed command finished (to be updated)
        with open(output_storage_file, "w") as output:
            output.write(printedStatus)

        print("--------------------------")
        print("Command finished " + printedStatus + "! Scroll up to check output (if any) if it exceeds the screen.")

def updateIndividualCommandHistoryFiles(command):
    c_r_hist_max_entries = 25

    with open(c_r_hist_file, "r") as c_r_hist:
        c_r_hist_content = []
        c_r_hist_entries = 0
        for entry in c_r_hist.readlines():
            c_r_hist_content.append(entry.strip('\n'))
            c_r_hist_entries = c_r_hist_entries + 1

    if command in c_r_hist_content:
        c_r_hist_content.remove(command)
    elif c_r_hist_entries == c_r_hist_max_entries:
        c_r_hist_content.remove(c_r_hist_content[c_r_hist_entries-1])
    c_r_hist_content = [command] + c_r_hist_content

    with open(c_r_hist_file, "w") as c_r_hist:
        for entry in c_r_hist_content:
            c_r_hist.write(entry+'\n')


executeNew()
