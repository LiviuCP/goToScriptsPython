import os
from os.path import isdir
import system_settings as sysset

def syncCurrentDir():
    assert os.path.isdir(sysset.fallback_dir), "Invalid fallback directory"
    fallbackPerformed = False
    currentDir = ""
    try:
        currentDir = os.getcwd()
    except BaseException as e:
        currentDir = sysset.fallback_dir.rstrip('/')
        os.chdir(currentDir)
        fallbackPerformed = True
    return (currentDir, fallbackPerformed)
