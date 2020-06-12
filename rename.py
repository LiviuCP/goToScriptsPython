import os, datetime, common, rename_backend as rn, display as out

def rename(chosenOption):
    def displayRenameInfo(chosenOption, valueToAdd = "", position = -1, nrOfRemovedCharacters = 0):
        assert chosenOption in rn.available_options, "The option argument is invalid"
        os.system("clear")
        print("1. Current directory:")
        print(os.getcwd())
        print("")
        print("2. Items contained (hidden ones are excluded):")
        print("")
        out.displayCurrentDirContent()
        print("")
        print("3. Renaming information")
        print("")
        print("Rename operation: " + rn.available_options_labels[chosenOption])
        valueToAddPrefix = "Initial numeric value" if chosenOption in {'A', 'P', 'I', 'R'} else "Value"
        print(valueToAddPrefix + " to add: " + valueToAdd) if len(valueToAdd) > 0 else print("", end='')
        print("Position: " + str(position)) if position >= 0 else print("", end='')
        print("Number of removed characters: " + str(nrOfRemovedCharacters)) if nrOfRemovedCharacters > 0 else print("", end='')
        print("")
    """
    This function should return a tuple consisting of following fields:
    - abort: True if user aborts entering rename params
    - string/initial number to be appended/prepended/inserted/used as replacement ("" if aborting)
    - insert/replace/delete position (-1 if no insert or abort)
    - number of deleted/replaced characters (0 if no such operation or abort)
    """
    def promptForRenameParameters(chosenOption):
        assert chosenOption in rn.available_options, "The option argument is invalid"
        # defaults
        shouldAbort = False
        valueToAdd = ""
        position = -1
        nrOfRemovedCharacters = 0
        isNumValueRequired = True if chosenOption in {'A', 'P', 'I', 'R'} else False
        shouldAbort = False
        if chosenOption != 'd':
            promptForValueToAdd = "Enter the " + ("numeric value" if isNumValueRequired else "fixed text string") + " to be added to " + ("first" if isNumValueRequired else "each") + " item name: "
            displayRenameInfo(chosenOption, valueToAdd, position, nrOfRemovedCharacters)
            requestedInput = common.getInputWithNumCondition(promptForValueToAdd, isNumValueRequired, lambda userInput: len(userInput) > 0 and int(userInput) <= 0, \
                                                         "Invalid input! A positive numeric value is required")
            shouldAbort = (len(requestedInput) == 0)
            if not shouldAbort:
                valueToAdd = requestedInput
        if not shouldAbort and chosenOption in {'i', 'I', 'd', 'r', 'R'}:
            displayRenameInfo(chosenOption, valueToAdd, position, nrOfRemovedCharacters)
            requestedInput = common.getInputWithNumCondition("Enter the position within the file name: ", True, lambda userInput: len(userInput) > 0 and int(userInput) < 0, \
                                                         "Invalid input! A non-negative numeric value is required")
            shouldAbort = (len(requestedInput) == 0)
            if not shouldAbort:
                position = int(requestedInput)
        if not shouldAbort and chosenOption in {'d', 'r', 'R'}:
            displayRenameInfo(chosenOption, valueToAdd, position, nrOfRemovedCharacters)
            requestedInput = common.getInputWithNumCondition("Enter the number of characters to be removed: ", True, lambda userInput: len(userInput) > 0 and int(userInput) <= 0, \
                                                         "Invalid input! A positive numeric value is required")
            shouldAbort = (len(requestedInput) == 0)
            if not shouldAbort:
                nrOfRemovedCharacters = int(requestedInput)
        return (shouldAbort, valueToAdd, position, nrOfRemovedCharacters)
    def simulateRenaming(renamingMap, chosenOption, buildParams):
        assert len(renamingMap) > 0, "Empty renaming map detected"
        assert chosenOption in rn.available_options, "The option argument is invalid"
        assert len(buildParams) == 3, "The number of renaming map build parameters is not correct"
        displayRenameInfo(chosenOption, buildParams[0], buildParams[1], buildParams[2])
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("Renaming of all items (except hidden ones) is about to proceed!")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("")
        print("Here a few examples about how the renamed items would look like:")
        print("")
        entryNumber = 0
        for key, value in renamingMap.items():
            print('{0:<40s} {1:<80s}'.format("Original:  " + key, "Renamed:  " + value))
            entryNumber += 1
            if entryNumber == rn.getRenamingSimulationLimit():
                break
        print("")
    def doRenameItems(renamingMap):
        assert len(renamingMap) > 0, "Empty renaming map detected"
        renamingDone = True #just to make sure the loop is executed at least once
        sortAscending = True #alternative sorting will be performed so a bi-directional passing of the dict keys is performed
        while renamingDone:
            renamingDone = False
            for entry in sorted(renamingMap.keys(), key = lambda k: k.lower(), reverse = not sortAscending):
                # we MUST ensure no renaming occurs if the map value is an existing current dir item, otherwise the it will get OVERWRITTEN and DATA IS LOST
                if len(renamingMap[entry]) > 0:
                    if not os.path.exists(renamingMap[entry]):
                        os.rename(entry, renamingMap[entry])
                        renamingMap[entry] = ""
                        renamingDone = True
                    # handle any possible (although with very low probability) swap of two item names ('A' gets renamed to 'B' and vice-versa) which might cause an infinite loop
                    elif renamingMap[renamingMap[entry]] == entry:
                        tempItemName = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                        os.rename(entry, tempItemName)
                        os.rename(renamingMap[entry], entry)
                        os.rename(tempItemName, renamingMap[entry])
                        print("Items " + entry + " and " + renamingMap[entry] + " swapped!") # these rare (if ever existing) situations need to be captured
                        renamingMap[renamingMap[entry]] = ""
                        renamingMap[entry] = ""
                        renamingDone = True
            sortAscending = not sortAscending #change direction
    assert chosenOption in rn.available_options, "The option argument is invalid"
    if rn.areRenameableItemsInCurrentDir():
        shouldRename = False
        status = 0 # default status, no errors
        renamingParams = promptForRenameParameters(chosenOption)
        assert len(renamingParams) == 4, "Incorrect number of tuple values"
        os.system("clear")
        if not renamingParams[0]:
            buildParams = (renamingParams[1], renamingParams[2], renamingParams[3])
            renamingMap = dict()
            status = rn.buildRenamingMap(chosenOption, buildParams, renamingMap)
            assert status in range(3), "Unknown status code for renaming map build"
            if status == 0:
                simulateRenaming(renamingMap, chosenOption, buildParams) # give the user a hint about how the renamed files will look like; a renaming decision is then expected from user
                decision = common.getInputWithTextCondition("Would you like to continue? (y - yes, n - no (exit)) ", lambda userInput: userInput.lower() not in {'y', 'n'}, \
                                                            "Invalid choice selected. Please try again")
                os.system("clear")
                if decision.lower() == 'y':
                    shouldRename = True
        if shouldRename:
            doRenameItems(renamingMap)
            print("Items renamed")
        elif status > 0:
            print("Cannot rename the items. " + rn.status_messages[status])
        else:
            print("Renaming aborted")
    else:
        print("The directory is empty or contains only hidden items. Cannot perform renaming")
