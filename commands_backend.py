import sys, os
import common, commands_settings as cmdset

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
        common.displayFormattedCmdFileContent(cHist.readlines(), 0, len(crHist.readlines()))

def displayFormattedPersistentCmdHistContent():
    with open(cmdset.c_hist_file, "r") as cHist, open(cmdset.c_r_hist_file, "r") as crHist:
        common.displayFormattedCmdFileContent(cHist.readlines(), len(crHist.readlines()))

def displayFormattedFilteredCmdHistContent(filteredContent, totalNrOfMatches):
    common.displayFormattedCmdFileContent(filteredContent, 0)
    print("")
    print("\tThe search returned " + str(totalNrOfMatches) + " match(es).")
    if totalNrOfMatches > len(filteredContent):
        print("\tFor better visibility only part of them are displayed. Please narrow the search if needed.")


""" command history update functions """
def updateCommandHistory(command):
    def updateIfAlreadyExecuted(updateDict, executedCommand):
        assert len(executedCommand) > 0, "Empty command argument detected"
        entryContainedInFile = False
        with open(cmdset.c_p_str_hist_file, "r") as cpStrHist, open (cmdset.c_p_num_hist_file, "r") as cpNumHist:
            cpStrHistList = cpStrHist.readlines()
            cpNumHistList = cpNumHist.readlines()
            assert len(cpStrHistList) == len(cpNumHistList), "The number of elements in c_p_str_hist_file is different from the number contained in c_p_num_hist_file"
            for entryNumber in range(len(cpStrHistList)):
                command = cpStrHistList[entryNumber].strip('\n')
                count =  cpNumHistList[entryNumber].strip('\n')
                if command == executedCommand:
                    updateDict[command] = int(count) + 1;
                    entryContainedInFile = True
                else:
                    updateDict[command] = int(count);
        return entryContainedInFile
    assert len(command) > 0, "Empty command argument detected"
    with open(cmdset.c_l_hist_file, "a") as clHist, open(cmdset.c_r_hist_file, "r") as crHist:
        crHistContent = []
        crHistEntries = 0
        for entry in crHist.readlines():
            crHistContent.append(entry.strip('\n'))
            crHistEntries = crHistEntries + 1
        if command in crHistContent:
            crHistContent.remove(command)
        elif crHistEntries == cmdset.c_r_hist_max_entries:
            crHistContent.remove(crHistContent[crHistEntries-1])
        crHistContent = [command] + crHistContent
        crHist.close()
        with open(cmdset.c_r_hist_file, "w") as crHist, open(cmdset.c_l_hist_file, "r") as clHist:
            for entry in crHistContent:
                crHist.write(entry+'\n')
            clHistContent = []
            for entry in clHist.readlines():
                clHistContent.append(entry.strip('\n'))
            clHist.close()
            # only update persistent command history files if the executed command is not being contained in the visit log for the current day
            if command not in clHistContent:
                with open(cmdset.c_l_hist_file, "a") as clHist:
                    clHist.write(command + "\n")
                    cpHistUpdateDict = {}
                    if not updateIfAlreadyExecuted(cpHistUpdateDict, command):
                        cpHistUpdateDict[command] = 1
                    common.writeBackToPermHist(cpHistUpdateDict, cmdset.c_p_str_hist_file, cmdset.c_p_num_hist_file, True)

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
