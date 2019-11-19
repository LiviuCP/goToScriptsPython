Thank you for downloading this script.

Please read this file prior to running it!

=====================================================

0. DISCLAIMER

This script was created for home use. It's primarily intended for geeks (like me) that enjoy using the CLI.

Do not use it on servers, business systems or other "critical" devices. It hasn't been tested thoroughly and there might still be some bugs.

To conclude, use it at your own risk. I will not be held accountable for any damage or loss it might cause whatsoever. 

Please let me know if you find any inconsistent information in this document so I can update it.

1. INTRODUCTION

This script file contains various functions that enable navigation through a UNIX-like file system.

It also performs history reporting and creating a list of favorite dirs. Both history and favorites can be used for easy navigation to any of the entries.

2. Supported systems

Currently it is only supported on Linux. It is planned to add Mac OS support in the future.

On the Linux version the "CLI-only" mode is supported. This means the script does not synchronize the current directory of the terminal with the one from the explorer window. The reason for this implementation is that there are several distributions of Linux and the explorer tool might be differ from one to another.

However a GUI mode might be available depending on distribution. For example on OpenSUSE it is possible to run the CLI-only script in a terminal embedded in the explorer window in KDE.

3. INSTALLATION

Clone from the repo, then follow these steps from either branch:

a. Ensure you have Python 3 installed. Check if /usr/bin/python3 exists.
b. Copy all Python files to the home directory. This looks pretty messy at the
moment but I will correct it. The python script is still under construction.
c. Create an alias for /usr/bin/python3 navigate.py in .bashrc
d. Temporary fix: create an empty file .store_output in the home
directory. This bug is planned to be fixed soon.
e. Restart the terminal once ready and start using the functionality by
executing the instruction mentioned at point c.

4. KNOWN ISSUES/BUGS

1) In some Linux implementations the there are empty lines between menu
entries. This is planned to be fixed soon.

2) When having directories like ./abcd and ./abcdefgh there are issues when
using wildcards. For example if using *ab to switch to either of these two an
error will occur and the cd will not be executed. A workaround is to type a*d
for switching to abcd or a*h for switching to abcdefgh. Also a good practice
that I recommend is not to create a folder that has its name string included
as first part of the string of another dir.

If any other bugs are discovered please feel free to comment on my Github page
(https://github.com/LiviuCP) or write me an e-mail (liviucst@gmail.com).

Please note that these scripts are currently in the initial phase, there are
still many changes to be done until they become "mature".

5. FUNCTIONALITY

Following features are contained in the script:
- navigation functionality for changing the current directory
- navigation history reporting
- storing directories in a favorites menu
- command executing functionality

To access these functions you need to execute the navigate.py script. These features will be detailed in the following sections.

5.1. The goto functionality

Enter navigation mode. Then enter the path of the directory to be visited.

You can enter:
- absolute paths
- relative paths
- paths with wildcards

If no argument is entered the user home directory will be visited.

5.2. The history and favorites menus

Enter navigation mode, then enter < for history or > for favorites.

The history menu keeps track of the:
- recently visited directories
- most visited directories

The favorites menu contains the directories the user previously added to the list of preferred folders. It is not limited in number of entries, however it's recommended to use it for storing the so called entry-point directories (like Desktop, Pictures, Documents, etc). It can also be used for storing paths to temporarily mounted filesystems (like SD cards). If accessing a temporary filesystem make sure it is mounted before doing any access attempt.

When choosing an entry (enter the number and press ENTER) from one of the two menus the chosen directory is automatically visited.

The menus are sorted alphabetically for easy identification of the required entry. 

It is possible to navigate to a specific entry without accessing the menus by entering operator < (for history) or > (for favorites) followed by the entry number in navigation mode. This is a great way of speeding up the access if the user knows "by heart" the entry number of the path to be visited. For example if directory /home/myUserName/Documents has entry number 2 in Favorites the user can enter >2 in navigation mode to visit it. No spaces should be entered between operator and the number. If the string after the operator is not a valid entry number the substring starting with the character after the operator will be considered a directory path and the script will attempt to visit it. If the path is invalid an error will be triggered.

If you cannot find a entry simply enter the required path(s) to navigate to the directory you wish to visit. It is not required to exit the history and favorites menus in order to do this. Any input other than the given range of numbers or the quit (!) is considered regular navigation input. I call this the "input forwarding feature". This feature is present in other menus too.

5.3. Visiting the previous directory

From the navigation menu enter the comma character (,) and press ENTER in order to achieve this. You can run this function as many times as you wish. The system will toggle between the two directories.

Note: if previously entering argument '.' the goToPrevDir function will re-visit the current directory. If no directory had been visited since entering the navigation mode the script will issue a warning and the current directory will remain unchanged.

5.4. Adding a directory to favorites

From navigation mode go to the directory you need to add to favorites. Then simply enter +> and press RETURN. Each directory can only be added once to the favorites menu.

Another way of adding the directory would be executing the addToFavorites function with the dir path as argument (both relative and absolute paths are allowed).

5.5. Removing a directory from favorites

From navigation mode enter -> and press RETURN. A menu will be opened. Choose the entry number of the directory to be removed from favorites. Any other input will be handled as normal navigation input by using the "input forwarding feature" that was previously mentioned.

5.6. Executing commands

It is possible to execute regular shell commands (like cd, ls, etc.) or other scripts from the navigation mode. 

In order to do this you just need to enter the : character followed by the actual command and press ENTER. For example in order to execute 'ls -l' enter ':ls -l'.

To repeat the last executed command just enter the :- characters and press ENTER.

To enter a new command by editing the previously executed one just enter : and press ENTER. This feature is only available on BASH4 so make sure to upgrade the shell in order to use it.

It is also possible to enter the command history menu by typing :< and pressing ENTER. Similar to navigation history by entering a valid number the chosen command is executed.

The command history can also be accessed in edit mode by entering :: and pressing ENTER. In edit mode when the number of a command is entered the string of the command is displayed for editing. After editing and pressing ENTER the new command will be executed. The command execution can be aborted by entering : at the end of the string and pressing ENTER. This feature is only available in BASH4. In BASH3 the menu can be accessed in edit mode however when entering the number of the command to be edited an error will be triggered.

To erase the command history enter ::<> and press ENTER. You will not be able to enter the command history menu if no entry is available.

Important note: in navigation mode make sure you launch time consuming commands in the background by using the ampersand (&) unless you need to visualize the output of the executed command on the screen.

5.7. Getting help

All possible navigation options can be viewed by entering the ? character followed by ENTER in navigation mode.

6. THE HISTORY FUNCTIONALITY

Each time a directory is visited, the event is tracked in a history file. There are four files where this tracking is done:
- the recent history file
- the persistent history file
- the consolidated history file
- the excluded history file

In addition to these a command history menu is available, that tracks the most recently executed shell commands in navigation mode. This is different from the standard BASH history as it only tracks the commands initiated in navigation mode, namely the ones preceded by the : character. Currently 2 files are being used for doing this tracking:
- the recent command history file
- the command history file (same as the recent command history file but sorted)

6.1. Recent history

Most recently visited directory paths are mentioned here.

6.2. Persistent history

All paths except the ones from excluded history are mentioned here along with the number of visits. When a new directory is visited the first time on the current day the number of visits is incremented. Further visits on the same day are not taken into account. This prevents unrealistic reporting which might occur if a directory has been entered many times during a day and then remains unvisited for a long time.

Also if the previous directory is the same with the visited directory the persistent history is not updated.

The file is sorted each time it is updated and the most visited paths are added to a consolidated history file.

6.3. Consolidated history

This file consolidates the entries contained in the previous 2 files. A unified interface is provided to the user for accessing the history.

6.4. Excluded history

When a directory is added to favorites its entry from the persistent history file is added to this file. This way the number of visits continues to be tracked (same tracking mechanism as for persistent history) and in the same time the path is separated from consolidated history.

When the directory is removed from favorites the entry is moved back to persistent history with the actual number of visits.

If the directory hadn't been visited prior to adding to favorites (e.g. if adding it by calling the addToFavorites function with the directory path as argument when in another directory) an entry with 0 visits is created in the excluded history file. If the directory is removed from favorites before visiting it the entry is removed both from favorites file and excluded history and nothing is added to persistent history. 

6.5. Command history

As the user executes commands in navigation mode each command is tracked in a dedicated history file. Up to a specific number of commands can be stored. This is determined by the cHistMaxRows variable.

The commands are stored "in order" but duplicates are not allowed. If the maximum number of entries has been reached the least recent command is taken out. The entries are displayed to the user in a sorted fashion so they can easily be found and executed. This occurs in a similar fashion to creating the recent history sub-menu.

It is possible to setup the minimum number of characters a command should contain in order to be stored in the command history file. This is done by setting up the minNrOfCmdChars variable. For example by setting minNrOfCmdChars=10 each command with less than 10 characters will be prevented from being included into the command history. The characters include the spaces but not the : character used for entering the command in navigation mode. This rule can be bypassed if more spaces are being included in the command (if the command has a single word the spaces shluld be added before the word).

For example:
:echo abcd #will not be included in command history (less than 10 characters - a total of 9, including space, excluding : )
:echo  abcd #will be included in command history (2 spaces this time)
:echo #will not be included, no matter how many spaces are entered after echo
:      echo #will be included, there is a total of 10 spaces, 6 spaces before the echo word

7. HANDLING MISSING DIRECTORIES

It can happen that for an entry chosen from one of the 2 above mentioned menus the path doesn't exist anymore. This can happen for various reasons:
- the directory has been deleted
- the directory has been moved, renamed or a combination of both

In this case the user has two options:
- remove the entry from the menus
- remap the path to an existing one (for example when the directory has been renamed) to preserve the number of visits

7.1. Removing the path

When this option is chosen the path is removed from all menus and files. The number of visits is lost.

7.2. Remapping

If the user chooses to remap the path to an existing one, two options are available:
- remap to a path that is not contained in favorites or consolidated history. In this case the path is replaced in the menus with the new path and the number of visits is kept.
- remap to a path that already exists in the menus. In this situation, the no more existing path is removed from the menus. The number of visits of the replacing path is updated only if the removed path had a greater number. For example if the removed path had 5 visits and the replacing path has 2 visits then the number of visits of the replacing path will be updated to 5. If the situation is viceversa it would be as if just removing the no more existing path (section 7.1).

8. MISCELLANEOUS

It is possible to erase all entries from history, which means all history files are cleared. When this happens there are no more entries in the consolidated history menu and viewing that menu is disabled (a warning will be issued by script). However the favorites menu retains its entries, yet the number of visits mentioned in excluded history is 0.

Type :<> in either history or favorites menus and hit ENTER in order to clear all history.