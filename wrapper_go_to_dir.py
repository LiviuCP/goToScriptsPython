import sys, os
from os.path import expanduser
import go_to_dir as gtdir

def wrapperGoTo():
    if len(sys.argv) == 1:
        gtdir.goTo()
    elif len(sys.argv) == 2:
        gtdir.goTo(sys.argv[1])
    else:
        gtdir.goTo(sys.argv[1], sys.argv[2])

wrapperGoTo()
