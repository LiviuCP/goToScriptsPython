import sys, os
import display_help as dhelp
import nav_menus_update as nav
import clear_command_history as clchist
import go_to_command_menu as gtcm
import execute_new_command as exnew
import wrapper_edit_and_exec_prev_command as weditexec
import wrapper_go_to_dir as wgtdir
import go_to_menu as gtm
from os.path import expanduser

home_dir = expanduser("~") + "/"
input_storage_file = home_dir + ".store_input"

# exit codes: 0 - no action performed (returned by default unless otherwise mentioned), 1 - forward input to BASH, 2 - update prevCommand and commandResult, 3 - no arguments, 4 - update prev dir and cd
def handle_nav_option(navigationInput, prevDir, prevCommand):
    if navigationInput == "?":
        dhelp.display()
    elif navigationInput == ":-":
        if prevCommand == "":
            print("No shell command previously executed")
        else:
            exnew.executeNew(prevCommand)
    elif navigationInput == ":":
        result = weditexec.wrapperEditExecPrevCmd(prevCommand)
        if result == 0:
            return 2
    elif navigationInput == ":<":
        result = gtcm.visit_command_menu("--execute")
        # update in BASH ...
        if result == 0:
            return 2
        elif result == 1:
            return 1
    elif navigationInput == "::":
        result = gtcm.visit_command_menu("--edit")
        if result == 0:
            return 2
        elif result == 1:
            return 1
    elif navigationInput == "::<>":
        clchist.clearHistory()
    elif navigationInput == "<":
        result = gtm.visit_nav_menu("-h", prevDir)
        if result == 0:
            return 4
        elif result == 1:
            return 1
    elif navigationInput == ">":
        result = gtm.visit_nav_menu("-f", prevDir)
        if result == 0:
            return 4
        elif result == 1:
            return 1
    elif len(navigationInput) > 1 and navigationInput[0] == "<":
        navInput = navigationInput[1:]
        result = gtm.visit_nav_menu("-h", prevDir, navInput)
        if result == 0:
            return 4
        elif result == 1:
            return 1
    elif len(navigationInput) > 1 and navigationInput[0] == ">":
        navInput = navigationInput[1:]
        result = gtm.visit_nav_menu("-f", prevDir, navInput)
        if result == 0:
            return 4
        elif result == 1:
            return 1
    elif navigationInput == ",":
        wgtdir.wrapperGoTo(prevDir, os.getcwd())
        return 4
    elif navigationInput == "+>":
        nav.addToFavorites()
    elif navigationInput == "->":
        returnCode = nav.removeFromFavorites()
        if returnCode == 2:
            return 1
    elif navigationInput == ":<>":
        nav.clearHist()
    elif navigationInput == "!":
        print("You exited navigation mode.")
    else:
        if navigationInput != "" and navigationInput[0] == ":":
            commandToExecute = navigationInput[1:]
            with open(input_storage_file, "w") as input_storage:
                input_storage.write(commandToExecute) # will be taken over by BASH as prev command
            exnew.executeNew(commandToExecute)
            return 2
        else:
            if navigationInput == "":
                wgtdir.wrapperGoTo()
            else:
                wgtdir.wrapperGoTo(navigationInput, prevDir)
            return 4
