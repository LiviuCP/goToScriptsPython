""" functions shared within navigation_backend.py and not used elsewhere """

import os
import navigation_settings as navset
from pathlib import Path

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

def removePathFromPermHistoryFile(strHistFile, numHistFile, pathToRemove):
    itemContainedInHistFile = False
    strHistListUpdated = []
    numHistListUpdated = []
    nrOfRemovedPathVisits = -1 #default value, path is not contained in the history file
    with open(strHistFile, "r") as strHist, open(numHistFile, "r") as numHist:
        strHistList = strHist.readlines()
        numHistList = numHist.readlines()
        assert len(strHistList) == len(numHistList), "The number of elements in the the string history file is different from the number contained in the numbers history file"
        for index in range(len(strHistList)):
            if strHistList[index].strip('\n') == pathToRemove:
                nrOfRemovedPathVisits = int(numHistList[index].strip('\n'))
            else:
                strHistListUpdated.append(strHistList[index])
                numHistListUpdated.append(numHistList[index])
        if nrOfRemovedPathVisits is not -1:
            strHist.close()
            numHist.close()
            with open(strHistFile, "w") as strHist, open(numHistFile, "w") as numHist:
                for index in range(len(strHistListUpdated)):
                    strHist.write(strHistListUpdated[index])
                    numHist.write(numHistListUpdated[index])
    return nrOfRemovedPathVisits

def displayFormattedNavFileContent(fileContent, firstRowNr = 0, limit = -1):
    nrOfRows = len(fileContent)
    assert nrOfRows > 0, "Attempt to display an empty navigation menu"
    limit = nrOfRows if limit < 0 or limit > nrOfRows else limit
    assert limit != 0, "Zero entries limit detected, not permitted"
    beginCharsToDisplayForDirName = navset.max_nr_of_item_name_chars // 2 #first characters to be displayed for a directory name exceeding the maximum number of chars to be displayed
    endCharsToDisplayForDirName = beginCharsToDisplayForDirName - navset.max_nr_of_item_name_chars #last characters to be displayed for a directory name exceeding the maximum number of chars to be displayed
    beginCharsToDisplayForPath = navset.max_nr_of_path_chars // 2 #first characters to be displayed for an absolute path exceeding the maximum number of chars to be displayed
    endCharsToDisplayForPath = beginCharsToDisplayForPath - navset.max_nr_of_path_chars #last characters to be displayed for an absolute path exceeding the maximum number of chars to be displayed
    if firstRowNr < limit and firstRowNr >= 0:
        print('{0:<5s} {1:<40s} {2:<40s} {3:<85s}'.format('', '- PARENT DIR -', '- DIR NAME -', '- DIR PATH -'))
        for rowNr in range(firstRowNr, limit):
            dirPath = fileContent[rowNr].strip('\n')
            dirName = os.path.basename(dirPath) if dirPath != "/" else "*root"
            parentDir = os.path.basename(str(Path(dirPath).parent))
            if len(parentDir) == 0:
                parentDir = "*root"
            elif len(parentDir)-1 > navset.max_nr_of_item_name_chars:
                parentDir = parentDir[0:beginCharsToDisplayForDirName] + "..." + parentDir[endCharsToDisplayForDirName-1:]
            if len(dirName)-1 > navset.max_nr_of_item_name_chars:
                dirName = dirName[0:beginCharsToDisplayForDirName] + "..." + dirName[endCharsToDisplayForDirName-1:]
            if len(dirPath)-1 > navset.max_nr_of_path_chars:
                dirPath = dirPath[0:beginCharsToDisplayForPath] + "..." + dirPath[endCharsToDisplayForPath-1:]
            print('{0:<5s} {1:<40s} {2:<40s} {3:<85s}'.format(str(rowNr+1), parentDir, dirName, dirPath))
