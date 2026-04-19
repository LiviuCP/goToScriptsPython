import os
from settings import system_settings as sysset

def syncCurrentDir():
    assert os.path.isdir(sysset.fallback_dir), "Invalid fallback directory"
    fallbackPerformed = False
    currentDir = ""
    shouldPerformFallback = False
    try:
        currentDir = os.getcwd()
        # this covers the situations where the fallback should be performed AFTER an operation initiated from CURRENT TERMINAL finished
        # fallback is performed if this operation rendered the current directory inaccessible (e.g. "rmdir [/path/to/current_dir]")
        shouldPerformFallback = not os.path.isdir(currentDir)
    except BaseException:
        shouldPerformFallback = True
    if shouldPerformFallback:
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
