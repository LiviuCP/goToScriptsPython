import sys, os
import choose_path_from_menu as menupath
import handle_missing_dir as hmdir
import go_to_dir as gtdir
from os.path import expanduser, isdir

home_dir = expanduser("~") + "/"
input_storage_file = home_dir + ".store_input"
output_storage_file = home_dir + ".store_output"

def visit_nav_menu():
    if len(sys.argv) < 3:
        print("Insufficient number of arguments")
        sys.exit(3)
    elif len(sys.argv) == 3:
        prevDir = sys.argv[2]
        dirPath = menupath.choosePath(sys.argv[1])
    else:
        prevDir = sys.argv[2]
        dirPath = menupath.choosePath(sys.argv[1], sys.argv[3])
    if dirPath == ":1":
        sys.exit(1) #forward user input
    elif dirPath == ":2":
        sys.exit(2)
    elif dirPath == ":4":
        sys.exit(4)
    elif dirPath != ":3":
        if not os.path.isdir(dirPath):
            result = hmdir.handleMissingDir(dirPath, sys.argv[1])
            if result == ":1":
                sys.exit(1) #forward user input
        else:
            gtdir.goTo(dirPath, prevDir)
            sys.exit(0)

visit_nav_menu()
