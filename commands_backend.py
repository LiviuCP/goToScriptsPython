import sys, os
import shared_cmd_functions as cs, nav_cmd_common as common, commands_settings as cmdset

""" command history menu init/access functions """
def initCmdMenus():
    #ensure all required files and dirs exist
    if not os.path.exists(cmdset.c_log_dir):
        os.makedirs(cmdset.c_log_dir)
    with open(cmdset.c_r_hist_file, "a") as crHist, open(cmdset.c_p_str_hist_file, "a") as cpStrHist, open(cmdset.c_p_num_hist_file, "a") as cpNumHist:
        crHist.close() # close, in use by limitEntriesNr()
        common.limitEntriesNr(cmdset.c_r_hist_file, cmdset.c_r_hist_max_entries)
        cpStrHist.close() # close, in use by consolidatedHistory()
        cpNumHist.close() # close, in use by consolidatedHistory()
        consolidateCommandHistory()

def chooseCommand(userInput):
    result = (":3", "", "")
    with open(cmdset.c_hist_file, "r") as cHist:
        result = common.getMenuEntry(userInput, cHist.readlines())
    return result

def chooseFilteredCommand(userInput, filteredContent):
    return common.getMenuEntry(userInput, filteredContent)

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
    common.updateHistory(command, cmdset.c_l_hist_file, cmdset.c_r_hist_file, cmdset.c_r_hist_max_entries, cmdset.c_p_str_hist_file, cmdset.c_p_num_hist_file)

def buildFilteredCommandHistory(filteredContent, filterKey):
    assert len(filterKey) > 0, "Invalid filter key found"
    nrOfMatches = 0
    with open(cmdset.c_p_str_hist_file, 'r') as cpStrHist:
        result = []
        for entry in cpStrHist.readlines():
            if filterKey.lower() in entry.lower():
                result.append(entry.strip('\n'))
                nrOfMatches = nrOfMatches + 1
        nrOfExposedEntries = nrOfMatches if nrOfMatches < cmdset.max_filtered_c_hist_entries else cmdset.max_filtered_c_hist_entries
        for index in range(nrOfExposedEntries):
            filteredContent.append(result[index])
    return nrOfMatches

def clearCommandHistory():
    with open(cmdset.c_r_hist_file, "w"), open(cmdset.c_p_str_hist_file, "w"), open(cmdset.c_p_num_hist_file, "w"), open(cmdset.c_hist_file, "w"), open(cmdset.c_l_hist_file, "w"):
        print("", end='')

def consolidateCommandHistory():
    with open(cmdset.c_r_hist_file, 'r') as crHist, open(cmdset.c_p_str_hist_file, 'r') as cpStrHist, open(cmdset.c_hist_file, 'w') as cHist:
        crHistEntries = crHist.readlines()
        crHistEntries.sort()
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
