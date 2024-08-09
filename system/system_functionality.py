import os
from settings import system_settings as sysset

def syncCurrentDir():
    assert os.path.isdir(sysset.fallback_dir), "Invalid fallback directory"
    fallbackPerformed = False
    currentDir = ""
    try:
        currentDir = os.getcwd()
    except BaseException:
        currentDir = sysset.fallback_dir.rstrip('/')
        os.chdir(currentDir)
        sysset.gui_sync_enabled = False
        fallbackPerformed = True
    return (currentDir, fallbackPerformed)

# These methods should only be used by GuiSyncManager

def setGuiSyncEnabled(enabled):
    sysset.gui_sync_enabled = enabled

def isGuiSyncEnabled():
    return sysset.gui_sync_enabled
