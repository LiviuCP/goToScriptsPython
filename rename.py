import os, common, rename_backend as rn

available_options = {'a', 'A', 'p', 'P', 'i', 'I', 'd', 'r', 'R'}
simulation_limit = 5 #number of files for which the renaming would be simulated

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
        while renamingDone:
            renamingDone = False
            for entry in sorted(renamingMap.items(), key = lambda k:(k[1], k[0].lower())):
                if len(entry[1]) > 0 and not os.path.exists(entry[1]):
                    os.rename(entry[0], entry[1])
                    renamingDone = True
                    renamingMap[entry[0]] = ""
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
    errorOccurred = False
    if len(choice) > 0:
        renamingParams = promptForRenameParameters(choice)
        assert len(renamingParams) == 4, "Incorrect number of tuple values"
        os.system("clear")
        if not renamingParams[0]:
            buildParams = (renamingParams[1], renamingParams[2], renamingParams[3])
            renamingMap = dict()
            rn.buildRenamingMap(choice, buildParams, renamingMap)
            if not rn.isRenamingMapValid(renamingMap):
                errorOccurred = True
            else:
                simulateRenaming(renamingMap) # give the user a hint about how the renamed files will look like; a renaming decision is then expected from user
                decision = common.getInputWithTextCondition("Would you like to proceed? (y - yes, n - no (exit)) ", lambda userInput: userInput.lower() not in {'y', 'n'}, \
                                                            "Invalid choice selected. Please try again")
                os.system("clear")
                if decision.lower() == 'y':
                    shouldRename = True
    if shouldRename:
        doRenameItems(renamingMap)
        print("Items renamed")
    elif errorOccurred:
        print("Cannot rename the items. Possible reasons: ")
        print(" - the directory is empty")
        print(" - an out-of-range position for insert/delete/replace has been provided")
        print(" - duplicate filenames are being created")
    else:
        print("Renaming aborted")
