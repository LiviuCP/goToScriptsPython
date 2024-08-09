import os
from system import system_functionality as sysfunc
from settings import system_settings as sysset
from .private import platform_specific as pls

class GuiSyncManager:
    def __init__(self):
        assert sysset.gui_sync_allowed, "GUI sync not supported with current OS!"
        self.syncWithGuiEnabled = False
        self.syncWithGuiInitialized = False
        self.guiSyncCommand = pls.buildGuiSyncCommand()
        assert self.guiSyncCommand is not None, "Invalid GUI sync command!"
        self.closeGuiCommand = pls.buildCloseGuiCommand()
        assert self.closeGuiCommand is not None, "Invalid close GUI command!"

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
