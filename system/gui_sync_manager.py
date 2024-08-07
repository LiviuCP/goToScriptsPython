import os
from system import system_functionality as sysfunc
from settings import system_settings as sysset

class GuiSyncManager:
    def __init__(self):
        self.syncWithFinderEnabled = False
        self.syncWithFinderInitialized = False
        self.finderSyncCommand = self.__buildFinderSyncCommand__()
        self.closeFinderCommand = self.__buildCloseFinderCommand__()

    def isSyncWithFinderEnabled(self):
        return self.syncWithFinderEnabled

    """ performs first Finder sync (when application gets launched) """
    def initSyncWithFinder(self):
        if not self.syncWithFinderInitialized:
            self.syncWithFinderInitialized = True
            self.syncWithFinderEnabled = sysfunc.isFinderSyncEnabled()
            if self.syncWithFinderEnabled:
                os.system(self.finderSyncCommand)

    """ toggles the synchronization of the terminal with Finder on/off """
    def toggleSyncWithFinder(self):
        assert self.syncWithFinderInitialized, "No initialization performed for Finder synchronization"
        sysfunc.setFinderSyncEnabled(not self.syncWithFinderEnabled)
        self.syncWithFinderEnabled = sysfunc.isFinderSyncEnabled()
        if self.syncWithFinderEnabled:
            print("Enabling Finder synchronisation...")
            os.system(self.finderSyncCommand)
        else:
            print("Disabling Finder synchronisation...")
            if sysset.close_finder_when_sync_off:
                os.system(self.closeFinderCommand)
        print("Done!")

    """ checks if synchronisation with Finder is valid and in-line with system settings; in case a fallback occurred restores the Finder sync to the fallback directory """
    def checkSyncWithFinder(self):
        if sysfunc.isFinderSyncEnabled():
            assert self.syncWithFinderEnabled, "Invalid Finder sync setting" # sync enabled through another channel, not by request issued to Navigation
        elif self.syncWithFinderEnabled: #fallback occurred, sync with Finder needs to be restored to fallback dir
            isRestoreSuccessful = self.__restoreFinderToFallbackDir__()
            if not isRestoreSuccessful:
                print("")
                print("Warning! Unable to restore Finder to fallback directory. Sync with Finder is disabled.")

    """ reopens Finder in current directory either when this gets changed or when refreshed """
    def reopenFinder(self):
        if self.syncWithFinderEnabled:
            os.system(self.finderSyncCommand)

    """ closes Finder and disables sync (e.g. when application gets closed) """
    def closeFinder(self):
        if self.syncWithFinderEnabled:
            self.syncWithFinderEnabled = False
            if sysset.close_finder_when_sync_off:
                os.system(self.closeFinderCommand)

    """ restores the Finder sync after fallback, fallback dir becomes current Finder dir """
    def __restoreFinderToFallbackDir__(self):
        assert self.syncWithFinderEnabled and not sysfunc.isFinderSyncEnabled(), "Invalid scenario, no fallback occured"
        success = False
        #os.system(nav.buildCloseFinderCommand())
        sysfunc.setFinderSyncEnabled(self.syncWithFinderEnabled)
        #ensure sync with Finder was re-enabled in system functionality (only then re-open Finder)
        self.syncWithFinderEnabled = sysfunc.isFinderSyncEnabled()
        if self.syncWithFinderEnabled:
            success = True
            os.system(self.finderSyncCommand)
        return success

    def __buildFinderSyncCommand__(self):
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

    def __buildCloseFinderCommand__(self):
        setDelays = "delayBeforeClose=0.1;" + "\n"
        closeFinder = "sleep $delayBeforeClose;" + "\n" + "osascript -e \'quit app \"Finder\"\';" + "\n"
        handleClosingError = "if [[ $? != 0 ]]; then echo \'An error occured when closing Finder\'; " + "\n" + "fi"
        closeFinderCommand = setDelays + closeFinder + handleClosingError
        return closeFinderCommand
