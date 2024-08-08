import os
from os.path import expanduser
from sys import platform

home_dir = expanduser("~") + "/"
fallback_dir = home_dir #directory used as fallback in case the current directory becomes unavailable (e.g. deleted externally)

gui_sync_allowed = platform == "darwin" # sync with GUI is only supported on MACOS at the moment (GUI = Finder)
gui_sync_enabled = False # this setting changes during application runtime when the sync is toggled on/off; however it should normally be set True either at startup or actively (per user request) during runtime
close_gui_when_sync_off = True # set this variable to False if Finder should stay open when sync is toggled to off via :s command

# MACOS specific settings
delay_before_finder_close = 0.1 # delay applied before closing Finder via OSAScript
delay_before_finder_reopen = 0.1 # delay applied before re-opening Finder to prevent any unwanted behavior
delay_after_finder_reopen = 0.9 # delay applied after re-opening Finder to avoid any unwanted behavior
delay_error_finder_reopen = 1.8 # delay applied in case Finder cannot be re-opened due to an error to prevent an early re-open attempt (and a new and maybe more serious error)

assert platform != "win32", "This application is not supported on Windows!"
assert os.path.isdir(fallback_dir), "Invalid fallback directory!"
