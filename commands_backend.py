import sys, os
import shared_cmd_functions as cs, nav_cmd_common as nvcdcmn, commands_settings as cmdset, system_settings as sysset

""" command history menu init/access functions """
def initCmdMenus():
    #ensure all required files and dirs exist
    if not os.path.exists(cmdset.c_log_dir):
        os.makedirs(cmdset.c_log_dir)
    with open(cmdset.c_r_hist_file, "a") as crHist, open(cmdset.c_p_str_hist_file, "a") as cpStrHist, open(cmdset.c_p_num_hist_file, "a") as cpNumHist:
        crHist.close() # close, in use by limitEntriesNr()
        nvcdcmn.limitEntriesNr(cmdset.c_r_hist_file, cmdset.c_r_hist_max_entries)
        cpStrHist.close() # close, in use by consolidatedHistory()
        cpNumHist.close() # close, in use by consolidatedHistory()
        consolidateCommandHistory()

def chooseCommand(userInput):
    result = (":3", "", "")
    with open(cmdset.c_hist_file, "r") as cHist:
        result = nvcdcmn.getMenuEntry(userInput, cHist.readlines())
    return result

def chooseFilteredCommand(userInput, filteredContent):
    return nvcdcmn.getMenuEntry(userInput, filteredContent)

def isCommandMenuEmpty():
    return os.path.getsize(cmdset.c_hist_file) == 0

def displayFormattedRecentCmdHistContent():
    with open(cmdset.c_hist_file, "r") as cHist, open(cmdset.c_r_hist_file, "r") as crHist:
        cs.displayFormattedCmdFileContent(cHist.readlines(), 0, len(crHist.readlines()))

def displayFormattedPersistentCmdHistContent():
    with open(cmdset.c_hist_file, "r") as cHist, open(cmdset.c_r_hist_file, "r") as crHist:
        cs.displayFormattedCmdFileContent(cHist.readlines(), len(crHist.readlines()))

def displayFormattedFilteredCmdHistContent(filteredContent, totalNrOfMatches):
    cs.displayFormattedCmdFileContent(filteredContent, 0)
    print("")
    print("\tThe search returned " + str(totalNrOfMatches) + " match(es).")
    if totalNrOfMatches > len(filteredContent):
        print("\tFor better visibility only part of them are displayed. Please narrow the search if needed.")


""" command history update functions """
def updateCommandHistory(command):
    assert len(command) > 0, "Empty command argument detected"
    nvcdcmn.updateHistory(command, cmdset.c_l_hist_file, cmdset.c_r_hist_file, cmdset.c_r_hist_max_entries, cmdset.c_p_str_hist_file, cmdset.c_p_num_hist_file)

def buildFilteredCommandHistory(filteredContent, filterKey):
    assert len(filterKey) > 0, "Empty filter key found"
    return nvcdcmn.buildFilteredHistory(filteredContent, filterKey, cmdset.c_p_str_hist_file, cmdset.max_filtered_c_hist_entries)

def clearCommandHistory():
    with open(cmdset.c_r_hist_file, "w"), open(cmdset.c_p_str_hist_file, "w"), open(cmdset.c_p_num_hist_file, "w"), open(cmdset.c_hist_file, "w"), open(cmdset.c_l_hist_file, "w"):
        print("", end='')

def consolidateCommandHistory():
    with open(cmdset.c_r_hist_file, 'r') as crHist, open(cmdset.c_p_str_hist_file, 'r') as cpStrHist, open(cmdset.c_hist_file, 'w') as cHist:
        crHistEntries = crHist.readlines()
        cpStrHistEntries = []
        limit = 0
        for entry in cpStrHist.readlines():
            cpStrHistEntries.append(entry)
            limit = limit + 1
            if limit == cmdset.c_p_hist_max_entries:
                break;
        cpStrHistEntries.sort()
        for entry in crHistEntries:
            cHist.write(entry)
        for entry in cpStrHistEntries:
            cHist.write(entry)

def isSensitiveCommand(command):
    assert len(command) > 0, "Empty command argument detected"
    isSensitive = False
    for keyword in cmdset.sensitive_commands_keywords:
        if keyword in command:
            isSensitive = True
            break
    return isSensitive

def getMinCommandSize():
    return cmdset.min_command_size

""" command execution helper functions """
def buildShellCommand(command):
    assert len(command) > 0, "Empty command argument detected"
    sourceConfigFileCmd = "source ~/.bashrc;" #include .bashrc to ensure the aliases and scripts work
    getExitCodeCmd = "echo $? > " + sysset.output_storage_file #exit code (used by Python to determine if the command finished successfully or not)
    shellCommandToExecute = sourceConfigFileCmd + "\n" + command + "\n" + getExitCodeCmd
    return shellCommandToExecute

def retrieveCommandExecResult():
    result = -1
    with open(sysset.output_storage_file, "r") as output:
        result = int(output.readline().strip('\n'))
    return result
