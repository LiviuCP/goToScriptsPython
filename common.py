import os
from os.path import expanduser

home_dir = expanduser("~") + "/"
input_storage_file = home_dir + ".store_input"
output_storage_file = home_dir + ".store_output"

# common code to be used by cmd_menus.update.py and nav_menus_update.py

def limitEntriesNr(file_path, max_entries):
    with open(file_path, "r") as f:
        file_content = f.readlines()
        file_entries = 0
        for entry in file_content:
            file_entries = file_entries + 1
    if file_entries > max_entries:
        with open(file_path, "w") as f:
            for entry_nr in range(0, max_entries):
                f.write(file_content[entry_nr])

def getOutput(user_input, content, menu_type):
    def isInputValid(user_input, content):
        is_valid = True
        if user_input.isdigit():
            int_input = int(user_input)
            if int_input > len(content) or int_input == 0:
                is_valid = False
        else:
            is_valid = False
        return is_valid
    if len(content) == 0:
        output = ":4"
    elif isInputValid(user_input, content):
        user_input = int(user_input) - 1
        output = content[user_input]
    elif user_input == '!':
        print("You exited " + menu_type + " menu!")
        output = ":2"
    else:
        output = ":1"
    return (output.strip("\n"), user_input, "")

# if a valid absolute path is fed as argument the unchanged path (without any ending '/') is returned
def getAbsoluteDirPath(dirPath):
    if dirPath == "":
        pathToAdd = os.getcwd()
    else:
        pathToAdd = dirPath
        with open(input_storage_file, "w") as input_storage:
            input_storage.write(pathToAdd)
        # build BASH command for retrieving the absolute path of the replacing dir (if exists)
        command = "input=`head -1 " + input_storage_file + "`; "
        command = command + "output=" + output_storage_file + "; "
        command = command + "cd $input 2> /dev/null; if [[ $? == 0  ]]; then pwd > \"$output\"; else echo :4 > \"$output\"; fi"
        os.system(command)
        with open(output_storage_file, "r") as output_storage:
            pathToAdd = output_storage.readline().strip('\n')
        if pathToAdd == ":4":
            pathToAdd = ""
    return pathToAdd

def getNumberOfLines(file_path):
    nrLines = 0
    with open(file_path, "r") as fPath:
        for entry in fPath.readlines():
            nrLines = nrLines + 1
    return nrLines

def displayFormattedNavFileContent(fileContent, firstRowNr = 0, limit = -1):
    nrOfRows = len(fileContent)
    limit = nrOfRows if limit < 0 or limit > nrOfRows else limit
    if firstRowNr < limit and firstRowNr >= 0:
        for rowNr in range(firstRowNr, limit):
            dirPath = fileContent[rowNr].strip('\n')
            print('{0:<10s} {1:<30s} {2:<160s}'.format(str(rowNr+1), os.path.basename(dirPath), dirPath))

def displayFormattedCmdFileContent(fileContent, firstRowNr = 0, limit = -1):
    nrOfRows = len(fileContent)
    limit = nrOfRows if limit < 0 or limit > nrOfRows else limit
    if firstRowNr < limit and firstRowNr >= 0:
        for rowNr in range(firstRowNr, limit):
            command = fileContent[rowNr].strip('\n')
            print('{0:<10s} {1:<140s}'.format(str(rowNr+1), command))
