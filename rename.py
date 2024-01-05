import os, datetime, common, system_functionality as sysfunc, rename_backend as rn, display as out

def rename(chosenOption):
    def displayRenameInfo(currentDir, chosenOption, valueToAdd = "", position = -1, nrOfRemovedCharacters = 0):
        assert chosenOption in rn.available_options, "The option argument is invalid"
        os.system("clear")
        print("1. Current directory:")
        print(currentDir)
        print("")
        print("2. Items contained (hidden ones are excluded):")
        print("")
        out.displayDirContent(currentDir)
        print("")
        print("3. Renaming information")
        print("")
        print(f"Rename operation: {rn.available_options_labels[chosenOption]}")
        valueToAddPrefix = "Initial numeric value" if chosenOption in {'A', 'P', 'I', 'R'} else "Value"
        print(f"{valueToAddPrefix} to add: {valueToAdd}") if len(valueToAdd) > 0 else print("", end='')
        print(f"Position: {str(position)}") if position >= 0 else print("", end='')
        print(f"Number of removed characters: {str(nrOfRemovedCharacters)}") if nrOfRemovedCharacters > 0 else print("", end='')
        print("")
    """
    This function should return a tuple consisting of following fields:
    - abort: True if user aborts entering rename params
    - string/initial number to be appended/prepended/inserted/used as replacement ("" if aborting)
    - insert/replace/delete position (-1 if no insert or abort)
    - number of deleted/replaced characters (0 if no such operation or abort)
    """
    def promptForRenameParameters(currentDir, chosenOption):
        assert chosenOption in rn.available_options, "The option argument is invalid"
        # defaults
        valueToAdd = ""
        position = -1
        nrOfRemovedCharacters = 0
        isNumValueRequired = True if chosenOption in rn.number_adding_options else False
        shouldAbort = False
        try:
            if chosenOption != 'd':
                promptForValueToAdd = "Enter the " + ("numeric value" if isNumValueRequired else "fixed text string") + " to be added to " + ("first" if isNumValueRequired else "each") + " item name: "
                displayRenameInfo(currentDir, chosenOption, valueToAdd, position, nrOfRemovedCharacters)
                requestedInput = common.getInputWithNumCondition(promptForValueToAdd, isNumValueRequired, lambda userInput: len(userInput) > 0 and int(userInput) <= 0, \
                                                                 "Invalid input! A positive numeric value is required")
                shouldAbort = (len(requestedInput) == 0)
                if not shouldAbort:
                    valueToAdd = requestedInput
            if not shouldAbort and chosenOption in rn.position_requiring_options:
                displayRenameInfo(currentDir, chosenOption, valueToAdd, position, nrOfRemovedCharacters)
                requestedInput = common.getInputWithNumCondition("Enter the position within the file name: ", True, lambda userInput: len(userInput) > 0 and int(userInput) < 0, \
                                                                 "Invalid input! A non-negative numeric value is required")
                shouldAbort = (len(requestedInput) == 0)
                if not shouldAbort:
                    position = int(requestedInput)
            if not shouldAbort and chosenOption in rn.string_removal_options:
                displayRenameInfo(currentDir, chosenOption, valueToAdd, position, nrOfRemovedCharacters)
                requestedInput = common.getInputWithNumCondition("Enter the number of characters to be removed: ", True, lambda userInput: len(userInput) > 0 and int(userInput) <= 0, \
                                                                 "Invalid input! A positive numeric value is required")
                shouldAbort = (len(requestedInput) == 0)
                if not shouldAbort:
                    nrOfRemovedCharacters = int(requestedInput)
        except (KeyboardInterrupt, EOFError):
            shouldAbort = True
        return (shouldAbort, valueToAdd, position, nrOfRemovedCharacters)
    def simulateRenaming(currentDir, renamingMap, chosenOption, buildParams):
        assert len(renamingMap) > 0, "Empty renaming map detected"
        assert chosenOption in rn.available_options, "The option argument is invalid"
        assert len(buildParams) == 3, "The number of renaming map build parameters is not correct"
        valueToAdd, position, nrOfRemovedCharacters = buildParams
        displayRenameInfo(currentDir, chosenOption, valueToAdd, position, nrOfRemovedCharacters)
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
                        print(f"Items {entry} and {renamingMap[entry]} swapped!") # these rare (if ever existing) situations need to be captured
                        renamingMap[renamingMap[entry]] = ""
                        renamingMap[entry] = ""
                        renamingDone = True
            sortAscending = not sortAscending #change direction
    syncedCurrentDir, fallbackPerformed = sysfunc.syncCurrentDir()
    assert not fallbackPerformed, "Current directory fallback not allowed, should have already been performed!"
    assert chosenOption in rn.available_options, "The option argument is invalid"
    if rn.areRenameableItemsInCurrentDir():
        shouldRename = False
        status = 0 # default status, no errors
        shouldAbort, valueToAdd, position, nrOfRemovedCharacters = promptForRenameParameters(syncedCurrentDir, chosenOption)
        os.system("clear")
        syncedCurrentDir, fallbackPerformed = sysfunc.syncCurrentDir() # sync required after user entered the renaming params (in case the current dir became inaccessible in the meantime)
        if not fallbackPerformed and not shouldAbort:
            buildParams = (valueToAdd, position, nrOfRemovedCharacters)
            renamingMap = dict()
            status = rn.buildRenamingMap(chosenOption, buildParams, renamingMap)
            assert status in range(3), "Unknown status code for renaming map build"
            if status == 0:
                simulateRenaming(syncedCurrentDir, renamingMap, chosenOption, buildParams) # give the user a hint about how the renamed files will look like; a renaming decision is then expected from user
                try:
                    decision = common.getInputWithTextCondition("Would you like to continue? (y - yes, n - no (exit)) ", lambda userInput: userInput.lower() not in {'y', 'n'}, \
                                                                "Invalid choice selected. Please try again")
                    syncedCurrentDir, fallbackPerformed = sysfunc.syncCurrentDir() # sync required after user decided for renaming (or not) after simulation (in case the current dir became inaccessible in the meantime)
                    if not fallbackPerformed and decision.lower() == 'y':
                        shouldRename = True
                except (KeyboardInterrupt, EOFError):
                    shouldRename = False
                os.system("clear")
        if fallbackPerformed:
            out.printFallbackMessage()
        elif shouldRename:
            doRenameItems(renamingMap)
            print("Items renamed")
        elif status > 0:
            print(f"Cannot rename the items. {rn.status_messages[status]}")
        else:
            print("Renaming aborted")
    else:
        print("The directory is empty or contains only hidden items. Cannot perform renaming")
