import os
from os.path import isdir
import system_settings as sysset

def syncCurrentDir():
    assert os.path.isdir(sysset.fallback_dir), "Invalid fallback directory"
    fallbackPerformed = False
    currentDir = ""
    try:
        currentDir = os.getcwd()
    except FileNotFoundError as e:
        currentDir = sysset.fallback_dir.rstrip('/')
        os.chdir(currentDir)
        sysset.finder_sync_enabled = False
        fallbackPerformed = True
    return (currentDir, fallbackPerformed)

def setFinderSyncEnabled(enabled):
    sysset.finder_sync_enabled = enabled

def isFinderSyncEnabled():
    return sysset.finder_sync_enabled
