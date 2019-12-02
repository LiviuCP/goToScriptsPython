import os

# functions shared within nav_menu_update.py and not used elsewhere

def sortFavorites(favFile): # to do: handle empty argument
    favDict = {}
    with open(favFile, "r") as fav:
        favFileContent = fav.readlines()
        for entry in favFileContent:
            entry = entry.strip('\n')
            favDict[entry] = os.path.basename(entry)
    with open(favFile, "w") as fav:
        for entry in sorted(favDict.items(), key = lambda k:(k[1].lower(), k[0])):
            fav.write(entry[0] + '\n')

def removePathFromTempHistoryFile(histFile, path): # to do: handle empty arguments
    itemContainedInHistFile = False
    histContent = []
    with open(histFile, "r") as hist:
        for entry in hist.readlines():
            if entry.strip('\n') == path:
                itemContainedInHistFile = True
            else:
                histContent.append(entry)
    if itemContainedInHistFile == True:
        with open(histFile, "w") as hist:
            for entry in histContent:
                hist.write(entry)
    return itemContainedInHistFile
