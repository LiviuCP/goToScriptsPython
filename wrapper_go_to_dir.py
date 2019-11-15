import sys, os
from os.path import expanduser
import go_to_dir as gtdir

def wrapperGoTo(dir1 = "", dir2 = ""):
    if dir1 == "" and dir2 == "":
        gtdir.goTo()
    elif dir2 == "":
        gtdir.goTo(dir1)
    else:
        gtdir.goTo(dir1, dir2)
