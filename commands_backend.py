import sys, os, datetime
import common
from os.path import expanduser

home_dir = expanduser("~") + "/"
c_hist_file = home_dir + ".command_history"
c_r_hist_file = home_dir + ".recent_command_history"
c_p_str_hist_file = home_dir + ".persistent_command_history_strings" # actual commands
c_p_num_hist_file = home_dir + ".persistent_command_history_numbers" # number of times each command was executed (each row should match a row from the c_p_str_hist_file)
c_r_hist_max_entries = 10
c_p_hist_max_entries = 15
c_log_dir = home_dir + ".goToCmdLogs/"
c_l_hist_file = c_log_dir + datetime.datetime.now().strftime("%Y%m%d")

""" command history menu init/access functions """
def initCmdMenus():
    #ensure all required files and dirs exist
    if not os.path.exists(c_log_dir):
        os.makedirs(c_log_dir)
    with open(c_r_hist_file, "a") as crHist, open(c_p_str_hist_file, "a") as cpStrHist, open(c_p_num_hist_file, "a") as cpNumHist:
        crHist.close() # close, in use by limitEntriesNr()
        common.limitEntriesNr(c_r_hist_file, c_r_hist_max_entries)
        cpStrHist.close() # close, in use by consolidatedHistory()
        cpNumHist.close() # close, in use by consolidatedHistory()
        consolidateCommandHistory()

def chooseCommand(userInput):
    with open(c_hist_file, "r") as cHist:
        return common.getMenuEntry(userInput, cHist.readlines())

def isCommandMenuEmpty():
    return os.path.getsize(c_hist_file) == 0

def displayFormattedRecentCmdHistContent():
    with open(c_hist_file, "r") as cHist, open(c_r_hist_file, "r") as crHist:
        common.displayFormattedCmdFileContent(cHist.readlines(), 0, len(crHist.readlines()))

def displayFormattedPersistentCmdHistContent():
    with open(c_hist_file, "r") as cHist, open(c_r_hist_file, "r") as crHist:
        common.displayFormattedCmdFileContent(cHist.readlines(), len(crHist.readlines()))

""" command history update functions """
def updateCommandHistory(command):
    def updateIfAlreadyExecuted(updateDict, executedCommand):
        with open(c_p_str_hist_file, "r") as cpStrHist, open (c_p_num_hist_file, "r") as cpNumHist:
            entryContainedInFile = False
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
    with open(c_l_hist_file, "a") as clHist, open(c_r_hist_file, "r") as crHist:
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
        crHist.close()
        with open(c_r_hist_file, "w") as crHist, open(c_l_hist_file, "r") as clHist:
            for entry in crHistContent:
                crHist.write(entry+'\n')
            clHistContent = []
            for entry in clHist.readlines():
                clHistContent.append(entry.strip('\n'))
            clHist.close()
            # only update persistent command history files if the executed command is not being contained in the visit log for the current day
            if command not in clHistContent:
                with open(c_l_hist_file, "a") as clHist:
                    clHist.write(command + "\n")
                    cpHistUpdateDict = {}
                    if not updateIfAlreadyExecuted(cpHistUpdateDict, command):
                        cpHistUpdateDict[command] = 1
                    with open(c_p_str_hist_file, "w") as cpStrHist, open(c_p_num_hist_file, "w") as cpNumHist:
                        for cmd, count in sorted(cpHistUpdateDict.items(), key = lambda k:(k[1], k[0].lower()), reverse = True):
                            cpStrHist.write(cmd + '\n')
                            cpNumHist.write(str(count) + '\n')

def clearCommandHistory():
    with open(c_r_hist_file, "w"), open(c_hist_file, "w"):
        print("", end='')

def consolidateCommandHistory():
    with open(c_r_hist_file, 'r') as crHist, open(c_p_str_hist_file, 'r') as cpStrHist, open(c_hist_file, 'w') as cHist:
        crHistEntries = crHist.readlines()
        crHistEntries.sort()
        cpStrHistEntries = []
        limit = 0
        for entry in cpStrHist.readlines():
            cpStrHistEntries.append(entry)
            limit = limit + 1
            if limit == c_p_hist_max_entries:
                break;
        cpStrHistEntries.sort()
        for entry in crHistEntries:
            cHist.write(entry)
        for entry in cpStrHistEntries:
            cHist.write(entry)
