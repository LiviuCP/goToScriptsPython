""" functions shared within nav_menu_update.py and not used elsewhere """

import os

def sortFavorites(favFile):
    assert len(favFile) > 0 and os.path.isfile(favFile), "Invalid favorites file"
    with open(favFile, "r") as fav:
        favDict = {}
        favFileContent = fav.readlines()
        for entry in favFileContent:
            entry = entry.strip('\n')
            favDict[entry] = os.path.basename(entry)
        fav.close()
        with open(favFile, "w") as fav:
            for entry in sorted(favDict.items(), key = lambda k:(k[1].lower(), k[0])):
                fav.write(entry[0] + '\n')

def removePathFromTempHistoryFile(histFile, path):
    assert len(histFile) > 0 and os.path.isfile(histFile), "Invalid consolidated history file"
    assert len(path) > 0, "Empty path detected"
    itemContainedInHistFile = False
    with open(histFile, "a") as hist:
        hist.close() #just make sure the file exists
        with open(histFile, "r") as hist:
            histContent = []
            for entry in hist.readlines():
                if entry.strip('\n') == path:
                    itemContainedInHistFile = True
                else:
                    histContent.append(entry)
            if itemContainedInHistFile:
                with open(histFile, "w") as hist:
                    for entry in histContent:
                        hist.write(entry)
    return itemContainedInHistFile
