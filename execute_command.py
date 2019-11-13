import sys, os, datetime
from os.path import expanduser
import consolidate_command_history as cons_comm_hist

home_dir = expanduser("~") + "/"
c_r_hist_file = home_dir + ".recent_command_history"
input_storage_file = home_dir + ".store_input"
output_storage_file = home_dir + ".store_output"
minNrOfCmdChars = 10

def execute(commandToExecute):
    if len(commandToExecute) >= minNrOfCmdChars:
        updateIndividualCommandHistoryFiles(commandToExecute)
        cons_comm_hist.consolidate()

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
    # forward input command to BASH for further usage
    with open(input_storage_file, "w") as input_storage:
        input_storage.write(commandToExecute)

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
