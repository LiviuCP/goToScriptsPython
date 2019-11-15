import sys, os
import edit_and_exec_prev_command as editprev

def wrapperEditExecPrevCmd(command = ""):
    if command == "":
        returnCode = editprev.edit_and_exec()
    else:
        returnCode = editprev.edit_and_exec(command)
    return returnCode # 0 - executed, 1 - aborted by user
