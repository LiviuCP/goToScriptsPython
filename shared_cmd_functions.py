""" functions shared within commands_backend.py and not used elsewhere """

def displayFormattedCmdFileContent(fileContent, firstRowNr = 0, limit = -1):
    nrOfRows = len(fileContent)
    assert nrOfRows > 0, "Attempt to display an empty command menu"
    limit = nrOfRows if limit < 0 or limit > nrOfRows else limit
    assert limit != 0, "Zero entries limit detected, not permitted"
    if firstRowNr < limit and firstRowNr >= 0:
        for rowNr in range(firstRowNr, limit):
            command = fileContent[rowNr].strip('\n')
            print('{0:<10s} {1:<140s}'.format(str(rowNr+1), command))
