import sys, os
import edit_and_exec_prev_command as editprev

def wrapperEditExecPrevCmd():
    if len(sys.argv) == 1:
        editprev.edit_and_exec()
    else:
        editprev.edit_and_exec(sys.argv[1])

wrapperEditExecPrevCmd()
