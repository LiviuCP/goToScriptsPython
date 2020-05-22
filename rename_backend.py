import os

available_options = {'a', 'A', 'p', 'P', 'i', 'I', 'd', 'r', 'R'}

def buildRenamingMap(choice, buildParams, renamingMap):
    def createRenamingString(filename, choice, buildParams):
        assert choice in available_options, "The choice argument is invalid"
        assert len(buildParams) == 3, "The number of rename map build parameters is not correct"
        assert len(filename) > 0, "Empty filename passed"
        result = ""
        currentValue = buildParams[0] # this value is used for modifying the first build param in case it needs to be incremented; it is returned to sender either modified (incremented) or unchanged
        if choice in {'A', 'P', 'I', 'R'}:
            assert currentValue.isdigit(), "Non-numeric value transmitted for incremental append"
        if choice in {'i', 'I', 'd', 'r', 'R'}:
            assert str(buildParams[1]).isdigit and buildParams[1] >= 0, "Invalid insert position parameter"
        if choice in {'d', 'r', 'R'}:
            assert str(buildParams[2]).isdigit and buildParams[2] > 0, "Invalid number of characters parameter"
            availableCharacters = len(filename) - buildParams[1] if buildParams[1] < len(filename) else 0
            nrOfCharacters = min(availableCharacters, buildParams[2])
        if choice in {'a', 'A'}:
            result = filename + currentValue
        elif choice in {'p', 'P'}:
            result = currentValue + filename
        elif choice in {'i', 'I'}:
            if buildParams[1] < len(filename):
                result = filename[0:buildParams[1]] + currentValue + filename[buildParams[1]:len(filename)]
        elif choice == 'd':
            if availableCharacters > 0:
                result = filename[0:buildParams[1]] + filename[(buildParams[1] + buildParams[2]):]
        elif choice in {'r', 'R'}:
            if availableCharacters > 0:
                strippedFilename = filename[0:buildParams[1]] + filename[(buildParams[1] + buildParams[2]):]
                result = strippedFilename[0:buildParams[1]] + currentValue + strippedFilename[buildParams[1]:len(strippedFilename)]
        if choice in {'A', 'P', 'I', 'R'}:
            number = int(currentValue) + 1
            currentValue = str(number)
        return (result, (currentValue, buildParams[1], buildParams[2]))
    assert choice in available_options, "The choice argument is invalid"
    assert len(buildParams) == 3, "The number of rename map build parameters is not correct"
    transmittedBuildParams = buildParams
    curDirItems = os.listdir(os.curdir)
    curDirItems.sort(key = lambda k: k.lower())
    for entry in curDirItems:
        # exclude hidden files/dirs to avoid accidentally renaming any essential item
        if not entry.startswith('.'):
            result = createRenamingString(entry, choice, transmittedBuildParams)
            if len(result[0]) > 0:
                renamingMap[entry] = result[0]
            transmittedBuildParams = result[1]

def isRenamingMapValid(renamingMap):
    isValid = False
    if len(renamingMap) > 0:
        valuesList = []
        for entry in renamingMap.items():
            valuesList.append(entry[1])
        if len(dict.fromkeys(valuesList)) == len(renamingMap):
            isValid = True
    return isValid
