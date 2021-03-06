import os, common, rename_settings as renset

available_options = {'a', 'A', 'p', 'P', 'i', 'I', 'd', 'r', 'R'}
number_adding_options = {'A', 'P', 'I', 'R'}
position_requiring_options =  {'i', 'I', 'd', 'r', 'R'}
string_removal_options = {'d', 'r', 'R'}
appending_options = {'a', 'A'}
prepending_options = {'p', 'P'}
inserting_options = {'i', 'I'}
replacing_options = {'r', 'R'}
deleting_option = 'd'

available_options_labels = {
    'a' : "append text",
    'A' : "append incremented numeric value",
    'p' : "prepend text",
    'P' : "prepend incremented numeric value",
    "i" : "insert text",
    "I" : "insert incremented numeric value",
    "d" : "delete text",
    "r" : "replace characters with text",
    "R" : "replace characters with incremented numeric value"
}

status_messages = [
    "Success",
    "Some items could not be renamed due to insufficient string size",
    "Duplicate items would result from renaming"
]

"""
Possible return codes:
    - 0: success, a valid map obtained
    - 1: unable to rename all items
    - 2: duplicate items result from renaming
"""
def buildRenamingMap(choice, buildParams, renamingMap):
    def createRenamingString(filename, choice, buildParams):
        assert choice in available_options, "The choice argument is invalid"
        assert len(buildParams) == 3, "The number of rename map build parameters is not correct"
        assert len(filename) > 0, "Empty filename passed"
        result = ""
        currentValue = buildParams[0] # this value is used for modifying the first build param in case it needs to be incremented; it is returned to sender either modified (incremented) or unchanged
        if choice in number_adding_options:
            assert currentValue.isdigit(), "Non-numeric value transmitted for incremental append"
        if choice in position_requiring_options:
            assert str(buildParams[1]).isdigit and buildParams[1] >= 0, "Invalid insert position parameter"
        if choice in string_removal_options:
            assert str(buildParams[2]).isdigit and buildParams[2] > 0, "Invalid number of characters parameter"
            availableCharacters = len(filename) - buildParams[1] if buildParams[1] < len(filename) else 0
            nrOfCharacters = min(availableCharacters, buildParams[2])
        if choice in appending_options:
            result = filename + currentValue
        elif choice in prepending_options:
            result = currentValue + filename
        elif choice in inserting_options:
            if buildParams[1] < len(filename):
                result = filename[0:buildParams[1]] + currentValue + filename[buildParams[1]:len(filename)]
        elif choice == deleting_option:
            if availableCharacters > 0:
                result = filename[0:buildParams[1]] + filename[(buildParams[1] + buildParams[2]):]
        elif choice in replacing_options:
            if availableCharacters > 0:
                strippedFilename = filename[0:buildParams[1]] + filename[(buildParams[1] + buildParams[2]):]
                result = strippedFilename[0:buildParams[1]] + currentValue + strippedFilename[buildParams[1]:len(strippedFilename)]
        if choice in number_adding_options:
            number = int(currentValue) + 1
            currentValue = str(common.addPaddingZeroes(str(number), len(buildParams[0])))
        return (result, (currentValue, buildParams[1], buildParams[2]))
    def isValidRenamingMap(renamingMap):
        isValid = False
        valuesList = []
        for entry in renamingMap.items():
            valuesList.append(entry[1])
        if len(dict.fromkeys(valuesList)) == len(renamingMap):
            isValid = True
        return isValid
    assert areRenameableItemsInCurrentDir(), "The current dir is empty or all items are hidden"
    assert choice in available_options, "The choice argument is invalid"
    assert len(buildParams) == 3, "The number of rename map build parameters is not correct"
    isNumericRenameRequested = True if choice in number_adding_options else False
    if isNumericRenameRequested:
        assert str(buildParams[0]).isdigit(), "Non-numeric value detected for numeric rename operation"
    status = 0 # default code, succesfull creation of renamingMap
    transmittedBuildParams = buildParams
    curDirItems = []
    # exclude hidden files/dirs to avoid accidentally renaming any essential item
    for entry in os.listdir(os.curdir):
        if not entry.startswith('.'):
            curDirItems.append(entry)
    curDirItems.sort(key = lambda k: k.lower())
    #fixed number of characters the numeric string should have (for fixed strings it doesn't matter so we set it 0) to have all numbers aligned
    requestedNrOfCharacters = len(str(int(buildParams[0]) + len(curDirItems) - 1))  if isNumericRenameRequested else 0
    if isNumericRenameRequested:
        transmittedBuildParams = (common.addPaddingZeroes(buildParams[0], requestedNrOfCharacters), buildParams[1], buildParams[2])
    resultingMap = dict()
    for entry in curDirItems:
        result = createRenamingString(entry, choice, transmittedBuildParams)
        if len(result[0]) > 0:
            resultingMap[entry] = result[0]
        transmittedBuildParams = result[1]
    if len(curDirItems) == len(resultingMap):
        if isValidRenamingMap(resultingMap):
            for key, value in resultingMap.items():
                renamingMap[key] = value
        else:
             status = 2
    else:
        status = 1
    return status

def areRenameableItemsInCurrentDir():
    result = False
    for entry in os.listdir(os.curdir):
        if not entry.startswith('.'):
            result = True
            break
    return result

def getRenamingSimulationLimit():
    return renset.simulation_limit
