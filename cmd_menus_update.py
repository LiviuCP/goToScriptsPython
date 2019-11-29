import sys, os, datetime
import common
from os.path import expanduser

home_dir = expanduser("~") + "/"
c_hist_file = home_dir + ".command_history"
c_r_hist_file = home_dir + ".recent_command_history"
output_storage_file = home_dir + ".store_output"
c_r_hist_max_entries = 25
minNrOfCmdChars = 10

# 1) Initialize command environment
def initCmdMenus():
    with open(c_r_hist_file, "a") as c_r_hist:
        c_r_hist.write("")
    # limit the number of entries from recent command history to the maximum allowed
    common.limitEntriesNr(c_r_hist_file, c_r_hist_max_entries)
    # will have a more important role once persistent command history will be implemented
    consolidateCommandHistory()

# 2) Choose command from menu

# The returned outcome could have following special values in the first field:
# :1 - user input to be forwarded as regular input (path name/command)
# :2 - user exited the command menu, returned to navigation mode
# :3 - invalid first argument
# :4 - no entries in command menu
def chooseCommand(userInput):
    with open(c_hist_file, "r") as cHist:
        cHistContent = cHist.readlines()
    return common.getOutput(userInput, cHistContent, "command")
def isCommandMenuEmpty():
    return os.path.getsize(c_hist_file) == 0
def displayFormattedCmdHistContent():
    with open(c_hist_file, "r") as cHist:
        common.displayFormattedCmdFileContent(cHist.readlines())

# 3) Execute command
def executeCommand(commandToExecute):
    # *** helper functions ***
    def updateIndividualCommandHistoryFiles(command):
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
    # *** actual function ***
    if len(commandToExecute) >= minNrOfCmdChars:
        updateIndividualCommandHistoryFiles(commandToExecute)
        consolidateCommandHistory()
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
    print("--------------------------")
    print("Command finished " + printedStatus + "! Scroll up to check output (if any) if it exceeds the screen.")
    return (0, commandToExecute, printedStatus)

# 4) Clear command history
def clearCommandHistory():
    with open(c_r_hist_file, "w") as c_r_hist:
        c_r_hist.write("")
    with open(c_hist_file, "w") as c_hist:
        c_hist.write("")
    print("Content of command history menu has been erased.")

# 5) Shared functions
def consolidateCommandHistory():
    with open(c_r_hist_file, 'r') as c_r_hist:
        c_r_hist_entries = c_r_hist.readlines()
        c_r_hist_entries.sort()
    # always ensure the file is cleared before (re-)consolidating history
    with open(c_hist_file, 'w') as c_hist:
        for entry in c_r_hist_entries:
            c_hist.write(entry)
