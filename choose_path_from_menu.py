import sys, os
from os.path import expanduser

home_dir = expanduser("~") + "/"
r_hist_file = home_dir + ".recent_history"
fav_file = home_dir + ".goto_favorites"
hist_file = home_dir + ".goto_history"
input_storage_file = home_dir + ".store_input"
output_storage_file = home_dir + ".store_output"

# The result returned by this method is stored into the .store_output file to be picked by the BASH script
# It can have following values: an absolute path or a specific code that indicates a certain behavior:
# :1 - user input stored in .store_input, to be picked and forwarded by BASH
# :2 - user exited the choose path dialog, no further actions
# :3 - invalid or missing first argument sys.argv[1]
# :4 - empty history or favorites file
def choosePath():
    path = ""
    outcome = "none"
    if len(sys.argv) == 1:
        print("no option provided")
        outcome = ":3"
    else:
        file_choice = sys.argv[1]
        already_provided_input = True if len(sys.argv) > 2 else False
        if file_choice == "-f": #favorites
            outcome = chooseEntryFromFavoritesMenu(already_provided_input)
        elif file_choice == "-h": #consolidated history
            outcome = chooseEntryFromHistoryMenu(already_provided_input)
        else:
            print("invalid option provided")
            outcome = ":3"
    with open(output_storage_file, "w") as output_storage:
        output_storage.write(outcome)

def chooseEntryFromHistoryMenu(already_provided_input):
    with open(hist_file, "r") as hist:
        hist_content = hist.readlines()
    if already_provided_input == False:
        os.system("clear")
        if len(hist_content) == 0:
            print("There are no entries in the history menu.")
            user_input = ""
        else:
            with open(r_hist_file, "r") as r_hist:
                r_hist_entries = len(r_hist.readlines())
            line_nr = 1
            print("NAVIGATION HISTORY")
            print("")
            print("-- RECENTLY VISITED DIRECTORIES --")
            print("")
            while line_nr <= r_hist_entries:
                entry = hist_content[line_nr-1].strip('\n')
                print('{0:<10s} {1:<30s} {2:<160s}'.format(str(line_nr), os.path.basename(entry), entry))
                line_nr = line_nr + 1
            print("")
            print("--  MOST VISITED DIRECTORIES --")
            print("")
            while line_nr <= len(hist_content):
                entry = hist_content[line_nr-1].strip('\n')
                print('{0:<10s} {1:<30s} {2:<160s}'.format(str(line_nr), os.path.basename(entry), entry))
                line_nr = line_nr + 1
            print("")
            print("Current directory: " + os.getcwd())
            print("")
            print("Enter the number of the directory you want to navigate to.")
            print("Enter ! to quit.")
            print("")

            # to update: enable path autocomplete
            user_input = input()
            os.system("clear")
    else:
        user_input = sys.argv[2]

    return getOutput(user_input, hist_content)

def chooseEntryFromFavoritesMenu(already_provided_input):
    with open(fav_file, "r") as fav:
        fav_content = fav.readlines()
    if already_provided_input == False:
        os.system("clear")
        if (len(fav_content) == 0):
            print("There are no entries in the favorites menu.")
            user_input = ""
        else:
            print("FAVORITE DIRECTORIES")
            print("")
            line_nr = 1
            for entry in fav_content:
                entry = entry.strip('\n')
                print('{0:<10s} {1:<30s} {2:<160s}'.format(str(line_nr), os.path.basename(entry), entry))
                line_nr = line_nr + 1
            print("")
            print("Current directory: " + os.getcwd())
            print("")
            print("Enter the number of the directory you want to navigate to.")
            print("Enter ! to quit.")
            print("")

            # to update: enable path autocomplete
            user_input = input()
            os.system("clear")
    else:
        user_input = sys.argv[2]

    return getOutput(user_input, fav_content)

def getOutput(user_input, content):
    if len(content) == 0:
        output = ":4"
    elif isValidInput(user_input, content):
        user_input = int(user_input) - 1
        output = content[user_input]
    elif user_input == '!':
        print("You exited history menu")
        output = ":2"
    else:
        # input to be forwarded for further handling to BASH
        with open(input_storage_file, "w") as input_storage:
            input_storage.write(user_input)
        output = ":1"
    return output

def isValidInput(user_input, content):
    is_valid = True
    if user_input.isdigit():
        int_input = int(user_input)
        if int_input > len(content) or int_input == 0:
            is_valid = False
    else:
        is_valid = False
    return is_valid

choosePath()
