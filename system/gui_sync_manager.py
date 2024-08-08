import os
from system import system_functionality as sysfunc
from settings import system_settings as sysset

class GuiSyncManager:
    def __init__(self):
        self.syncWithGuiEnabled = False
        self.syncWithGuiInitialized = False
        self.guiSyncCommand = self.__buildGuiSyncCommand__()
        self.closeGuiCommand = self.__buildCloseGuiCommand__()
        assert sysset.gui_sync_allowed

    def isSyncWithGuiEnabled(self):
        return self.syncWithGuiEnabled

    """ performs first GUI (explorer) sync (when application gets launched) """
    def initSyncWithGui(self):
        if not self.syncWithGuiInitialized:
            self.syncWithGuiInitialized = True
            self.syncWithGuiEnabled = sysfunc.isGuiSyncEnabled()
            if self.syncWithGuiEnabled:
                os.system(self.guiSyncCommand)

    """ toggles the synchronization of the terminal with GUI on/off """
    def toggleSyncWithGui(self):
        assert self.syncWithGuiInitialized, "No initialization performed for GUI synchronization"
        sysfunc.setGuiSyncEnabled(not self.syncWithGuiEnabled)
        self.syncWithGuiEnabled = sysfunc.isGuiSyncEnabled()
        if self.syncWithGuiEnabled:
            print("Enabling GUI synchronisation...")
            os.system(self.guiSyncCommand)
        else:
            print("Disabling GUI synchronisation...")
            if sysset.close_gui_when_sync_off:
                os.system(self.closeGuiCommand)
        print("Done!")

    """ checks if synchronisation with GUI is valid and in-line with system settings; in case a fallback occurred restores the GUI sync to the fallback directory """
    def checkSyncWithGui(self):
        if sysfunc.isGuiSyncEnabled():
            assert self.syncWithGuiEnabled, "Invalid GUI sync setting" # sync enabled through another channel, not by request issued to Navigation
        elif self.syncWithGuiEnabled: #fallback occurred, sync with GUI needs to be restored to fallback dir
            isRestoreSuccessful = self.__restoreGuiToFallbackDir__()
            if not isRestoreSuccessful:
                print("")
                print("Warning! Unable to restore GUI to fallback directory. Sync with GUI is disabled.")

    """ reopens GUI in current directory either when this gets changed or when refreshed """
    def reopenGui(self):
        if self.syncWithGuiEnabled:
            os.system(self.guiSyncCommand)

    """ closes GUI and disables sync (e.g. when application gets closed) """
    def closeGui(self):
        if self.syncWithGuiEnabled:
            self.syncWithGuiEnabled = False
            if sysset.close_gui_when_sync_off:
                os.system(self.closeGuiCommand)

    """ restores the GUI sync after fallback, fallback dir becomes current GUI dir """
    def __restoreGuiToFallbackDir__(self):
        assert self.syncWithGuiEnabled and not sysfunc.isGuiSyncEnabled(), "Invalid scenario, no fallback occured"
        success = False
        os.system(self.closeGuiCommand)
        sysfunc.setGuiSyncEnabled(self.syncWithGuiEnabled)
        #ensure sync with GUI was re-enabled in system functionality (only then re-open GUI)
        self.syncWithGuiEnabled = sysfunc.isGuiSyncEnabled()
        if self.syncWithGuiEnabled:
            success = True
            os.system(self.guiSyncCommand)
        return success

    def __buildGuiSyncCommand__(self):
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

    def __buildCloseGuiCommand__(self):
        setDelays = "delayBeforeClose=0.1;" + "\n"
        closeFinder = "sleep $delayBeforeClose;" + "\n" + "osascript -e \'quit app \"Finder\"\';" + "\n"
        handleClosingError = "if [[ $? != 0 ]]; then echo \'An error occured when closing Finder\'; " + "\n" + "fi"
        closeFinderCommand = setDelays + closeFinder + handleClosingError
        return closeFinderCommand
