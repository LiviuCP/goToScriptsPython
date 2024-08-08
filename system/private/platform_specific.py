from sys import platform
from settings import system_settings as sysset

def buildGuiSyncCommand():
    def buildMacOsGuiSyncCommand():
        setDelays = "delayBeforeClose=" + str(sysset.delay_before_finder_close) + ";" + "\n" + \
            "delayBeforeReopen=" + str(sysset.delay_before_finder_reopen) + ";" + "\n" + \
            "delayAfterReopen=" + str(sysset.delay_after_finder_reopen) + ";" + "\n" + \
            "delayErrorReopen=" + str(sysset.delay_error_finder_reopen) + ";" + "\n"
        closeFinder = "sleep $delayBeforeClose;" + "\n" + "osascript -e \'quit app \"Finder\"\';" + "\n"
        handleClosingError = "if [[ $? != 0 ]]; then echo \'An error occured when closing Finder\'; " + "\n"
        reopenFinder = "else sleep $delayBeforeReopen; open . 2> /dev/null;" + "\n"
        handleReopeningError = "if [[ $? != 0 ]]; then sleep $delayErrorReopen; echo \'An error occured when opening the new directory in Finder\'; " + "\n"
        addDelayAfterSuccessfulReopen = "else sleep $delayAfterReopen;" + "\n" + "fi" + "\n" + "fi" + "\n"
        openTerminal = "open -a terminal;"
        finderSyncCommand = setDelays + closeFinder + handleClosingError + reopenFinder + handleReopeningError + addDelayAfterSuccessfulReopen + openTerminal
        return finderSyncCommand
    guiSyncCommand = None
    if platform == "darwin":
        guiSyncCommand = buildMacOsGuiSyncCommand()
    return guiSyncCommand

def buildCloseGuiCommand():
    def buildMacOsCloseGuiCommand():
        setDelays = "delayBeforeClose=0.1;" + "\n"
        closeFinder = "sleep $delayBeforeClose;" + "\n" + "osascript -e \'quit app \"Finder\"\';" + "\n"
        handleClosingError = "if [[ $? != 0 ]]; then echo \'An error occured when closing Finder\'; " + "\n" + "fi"
        closeFinderCommand = setDelays + closeFinder + handleClosingError
        return closeFinderCommand
    closeGuiCommand = None
    if platform == "darwin":
        closeGuiCommand = buildMacOsCloseGuiCommand()
    return closeGuiCommand
