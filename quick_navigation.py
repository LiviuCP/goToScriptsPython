import shared_nav_functions as ns, navigation_settings as navset

def displayFormattedQuickNavigationHistory():
    with open(navset.r_hist_file, "r") as rHist:
        ns.displayFormattedNavFileContent(rHist.readlines(), 0, navset.q_hist_max_entries)

# a positive result guarantees validity of user provided quick navigation history entry
def isValidEntryNr(userInput):
    isValid = False
    if len(userInput) > 0 and userInput.isdigit():
        quickNavEntryNr = int(userInput)
        if quickNavEntryNr <= navset.q_hist_max_entries and quickNavEntryNr > 0:
            rHistEntriesCount = 0
            with open(navset.r_hist_file, "r") as rHist:
                rHistEntriesCount = len(rHist.readlines())
            isValid = quickNavEntryNr <= rHistEntriesCount
    return isValid
