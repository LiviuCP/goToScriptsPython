import os, datetime, common, rename_backend as rn

available_options = {'a', 'A', 'p', 'P', 'i', 'I', 'd', 'r', 'R'}
simulation_limit = 5 #number of files for which the renaming would be simulated
statusMessages = [
    "Success",
    "Some items could not be renamed due to insufficient string size",
    "Duplicate items would result from renaming"
]


def rename():
    """
    This function should return a tuple consisting of following fields:
    - abort: True if user aborts entering rename params
    - string/initial number to be appended/prepended/inserted/used as replacement ("" if aborting)
    - insert/replace/delete position (-1 if no insert or abort)
    - number of deleted/replaced characters (0 if no such operation or abort)
    """
    def promptForRenameParameters(chosenOption):
        assert chosenOption in available_options, "The option argument is invalid"
        # defaults
        shouldAbort = False
        valueToAdd = ""
        position = -1
        nrOfRemovedCharacters = 0
        isNumValueRequired = True if chosenOption in {'A', 'P', 'I', 'R'} else False
        shouldAbort = False
        if chosenOption != 'd':
            requestedInput = common.getInputWithNumCondition("Enter the value to be added: ", isNumValueRequired, lambda userInput: len(userInput) > 0 and int(userInput) <= 0, \
                                                         "Invalid input! A positive numeric value is required")
            shouldAbort = (len(requestedInput) == 0)
            if not shouldAbort:
                valueToAdd = requestedInput
        if shouldAbort == False and chosenOption in {'i', 'I', 'd', 'r', 'R'}:
            requestedInput = common.getInputWithNumCondition("Enter the position within the file name: ", True, lambda userInput: len(userInput) > 0 and int(userInput) < 0, \
                                                         "Invalid input! A non-negative numeric value is required")
            shouldAbort = (len(requestedInput) == 0)
            if not shouldAbort:
                position = int(requestedInput)
        if shouldAbort == False and chosenOption in {'d', 'r', 'R'}:
            requestedInput = common.getInputWithNumCondition("Enter the number of characters to be removed: ", True, lambda userInput: len(userInput) > 0 and int(userInput) <= 0, \
                                                         "Invalid input! A positive numeric value is required")
            shouldAbort = (len(requestedInput) == 0)
            if not shouldAbort:
                nrOfRemovedCharacters = int(requestedInput)
        return (shouldAbort, valueToAdd, position, nrOfRemovedCharacters)
    def simulateRenaming(renamingMap):
        assert len(renamingMap) > 0, "Empty renaming map detected"
        print("Here is how the renamed items would look like:")
        print("")
        entryNumber = 0
        for key, value in renamingMap.items():
            print("Original: " + key + "\tRenamed: " + value)
            entryNumber += 1
            if entryNumber == simulation_limit:
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
    if rn.areRenameableItemsInCurrentDir():
        isOptionValid = False
        choice = ""
        while isOptionValid == False:
            print("Following options are available for batch renaming:")
            print("")
            print("a - append string to each filename")
            print("A - append incrementing number to each filename")
            print("p - prepend string to each filename")
            print("P - prepend incrementing number to each filename")
            print("i - insert string into each filename")
            print("I - insert incrementing number into each filename")
            print("d - delete a substring from each filename")
            print("r - replace a substring from each filename with a substring")
            print("R - replace a substring from each filename with an incrementing number")
            print("At any time in the dialog press ENTER to quit")
            print("")
            choice = input("Enter the required option: ")
            os.system("clear")
            if len(choice) > 0 and choice not in available_options:
                print("Invalid option selected")
                print("")
            else:
                isOptionValid = True
        shouldRename = False
        status = 0 # default status, no errors
        if len(choice) > 0:
            renamingParams = promptForRenameParameters(choice)
            assert len(renamingParams) == 4, "Incorrect number of tuple values"
            os.system("clear")
            if not renamingParams[0]:
                buildParams = (renamingParams[1], renamingParams[2], renamingParams[3])
                renamingMap = dict()
                status = rn.buildRenamingMap(choice, buildParams, renamingMap)
                assert status in range(3), "Unknown status code for renaming map build"
                if status == 0:
                    simulateRenaming(renamingMap) # give the user a hint about how the renamed files will look like; a renaming decision is then expected from user
                    decision = common.getInputWithTextCondition("Would you like to proceed? (y - yes, n - no (exit)) ", lambda userInput: userInput.lower() not in {'y', 'n'}, \
                                                            "Invalid choice selected. Please try again")
                    os.system("clear")
                    if decision.lower() == 'y':
                        shouldRename = True
        if shouldRename:
            doRenameItems(renamingMap)
            print("Items renamed")
        elif status > 0:
            print("Cannot rename the items. " + statusMessages[status])
        else:
            print("Renaming aborted")
    else:
        print("The directory is empty or contains only hidden items. Cannot perform renaming")
