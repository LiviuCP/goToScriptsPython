import sys, os, datetime
import common
from os.path import expanduser

home_dir = expanduser("~") + "/"
c_hist_file = home_dir + ".command_history"
c_r_hist_file = home_dir + ".recent_command_history"
output_storage_file = home_dir + ".store_output"
c_r_hist_max_entries = 25
min_nr_of_cmd_chars = 10

# 1) Initialize command environment
def initCmdMenus():
    with open(c_r_hist_file, "a") as crHist:
        crHist.write("")
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
        with open(c_r_hist_file, "r") as crHist:
            crHistContent = []
            crHistEntries = 0
            for entry in crHist.readlines():
                crHistContent.append(entry.strip('\n'))
                crHistEntries = crHistEntries + 1
        if command in crHistContent:
            crHistContent.remove(command)
        elif crHistEntries == c_r_hist_max_entries:
            crHistContent.remove(crHistContent[crHistEntries-1])
        crHistContent = [command] + crHistContent
        with open(c_r_hist_file, "w") as crHist:
            for entry in crHistContent:
                crHist.write(entry+'\n')
    # *** actual function ***
    if len(commandToExecute) >= min_nr_of_cmd_chars:
        updateIndividualCommandHistoryFiles(commandToExecute)
        consolidateCommandHistory()
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
    return (0, commandToExecute, printedStatus)

# 4) Clear command history
def clearCommandHistory():
    with open(c_r_hist_file, "w") as crHist:
        crHist.write("")
    with open(c_hist_file, "w") as cHist:
        cHist.write("")

# 5) Shared functions
def consolidateCommandHistory():
    with open(c_r_hist_file, 'r') as crHist:
        crHistEntries = crHist.readlines()
        crHistEntries.sort()
    # always ensure the file is cleared before (re-)consolidating history
    with open(c_hist_file, 'w') as cHist:
        for entry in crHistEntries:
            cHist.write(entry)
