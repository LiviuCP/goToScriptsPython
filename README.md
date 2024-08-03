Thank you for downloading this script application.

Please read this file prior to running it!

=====================================================

0. DISCLAIMER

This script was created for home use. It's primarily intended for geeks (like me) that enjoy using the command line.

Do not use it on servers, business systems or other critical devices. It hasn't been tested thoroughly and there might still be some bugs.

To conclude, use it at your own risk. I will not be held accountable for any damage or loss it might cause whatsoever. 

Please let me know if you find any inconsistent information in this document so I can update it.

1. INTRODUCTION

This script contains functionality that enables:
- navigation through a UNIX-like file system.
- executing shell commands
- other useful actions like: CLI clipboard, recursive move/copy, batch renaming of files

It also performs history reporting (both for visited directories and commands) and creating a list of favorite dirs. Both navigation history and favorites can be used for easy navigation to any of the entries while commands history can be employed for executing any of stored commands.

2. SUPPORTED OPERATING SYSTEMS

The script is supported both on Linux and MacOS. It is not supported on Windows.

The pre-requisites for running it correctly are:
- Python 3.6 (minimum version)
- BASH/ZSH CLI

On MacOS the Anaconda navigator should be also be installed in order to ensure the script works properly.

Following should be noted for each supported OS:

1) On the Linux version the "CLI-only" mode is supported. This means the script does not synchronize the current directory of the terminal with one from the GUI explorer window. The reason for this implementation is that there are several distributions of Linux and the explorer tool might be differ from one to another.

2) On the MacOS version the terminal can be synchronized with a Finder window. This occurs as follows: when a valid path is entered in the terminal, the Finder will close and the re-open in the directory for which the path has been entered. This occurs no matter if the path is the same with the old one or not and this behavior has been implemented as the user might sometimes need to refresh the Finder window. The possible reason for requiring Finder refresh is mentioned in section 4. By default the sync feature is disabled but it can be enabled by entering option :s (+hit ENTER). To disable it enter :s again and hit the ENTER key. It is possible to enable synchronization at application startup by setting the finder_sync_enabled setting to True in system_settings.py. However this isn't recommended as it might slow the performance of the navigation process. Also, when closing the application the Finder sync is disabled and the Finder window is closed.

3. INSTALLATION

For Linux use the master or linuxScript branch to download the script. For MacOS the macOsScript branch is the most appropriate one (the other branches work as well, yet without Finder sync). Clone from the repo, switch to the chosen branch and follow these steps:

a. Ensure you have Python 3 installed (on Mac OS install Anaconda). Check whether /usr/bin/python3 exists. Minimum required Python version is 3.6.
b. Create an alias for the command '/usr/bin/python3 [absolute_path_of_cloned_repo]/goto_app.py' in .bashrc (or .zshrc). On Mac OS, after installing Anaconda it is sufficient to enter the keyword 'python' instead of /usr/bin/python3 in the command.
c. Open a new terminal window/tab and start using the functionality by executing the command alias mentioned at previous point.
d. Before shutting down the machine, in order to prevent forceful terminal closure, exit the script by entering the exit key (character '!') and pressing ENTER. Alternatively the CTRL+C or CTRL+D keyboard combination can be used.

4. KNOWN ISSUES/BUGS

1) Depending on terminal size, there might be empty lines between history or favorites menu entries. To correct this, you just need to resize the terminal until the spaces disappear. On MacOS it is possible to setup a pre-defined terminal size (number of lines/columns). Also due to the verbosity of the application (especially when quick history is enabled), it might be a good idea to choose larger terminal dimensions than usually needed in order to accomodate output "spikes". Nevertheless if these "spikes" still exceed the window size, the user would have to scroll up/down the window in order to carefully check application output.

2) When having directories like ./abcd and ./abcdefgh, there might be issues when using wildcards. For example, if using *ab to switch to either of these two, an error will occur and the change dir command will not be completed. A workaround is to type a*d for switching to abcd or a*h for switching to abcdefgh. Also a good practice that I recommend is (as much as possible) not to create a folder the name of which is a substring of another directory name.

3) Sometimes when having the Finder re-opened, the window is in an inactive state and the user cannot navigate it by using the arrow keys. To correct this, initiate a new re-opening in the current directory by entering '.' and pressing ENTER (or enter the :s option to disable and then again to re-enable Finder sync). Also for performance reasons it is recommended to disable the sync if one doesn't necessarily need to use the Finder.

If any other bugs are spotted, please feel free to report them on my Github page: https://github.com/LiviuCP.

5. FUNCTIONALITY

Following features are contained within script:
- navigation functionality for changing the current directory to the chosen one
- navigation history reporting
- storing preferred paths in a favorites menu
- command executing functionality
- command history reporting
- history and favorites filtering
- quick history for navigation and commands
- CLI clipboard
- recursive move/copy of files/directories to a chosen target directory
- batch renaming of files/directories

To access this functionality the goto_app.py script should be launched into execution. These features will be detailed in the following sections.

For more information regarding the navigation history/favorites and commands history please also check section 6.

5.1. The goto functionality

Enter the app by executing goto_app.py with Python. Then in the input section enter the path of the directory to be visited. No cd command keyword is required, entering the path will suffice.

You can enter:
- absolute paths
- relative paths (including ~ for home directory)
- paths with wildcards
- ancestor paths (see section 5.3.2)

Notes:
1) If no argument is entered the user home directory is set as target.
2) If the same directory as the current one is entered, although the current directory remains unchanged the Finder is refreshed when sync mode is enabled (MacOS only).

5.2. The navigation history and favorites menus

Enter navigation mode, then enter < for history or > for favorites.

The history menu keeps track of the:
- recently visited directories (a.k.a. recent history)
- most visited directories (a.k.a. persistent history)

The favorites menu contains the directories the user previously added to the list of preferred folders. The maximum number of entries is not limited, however it's recommended to use it for storing the so called entry-point directories (like Desktop, Pictures, Documents, etc). It can also be used for storing paths to temporarily mounted filesystems (like SD cards). When accessing a temporary filesystem, make sure it is mounted before doing any access attempt.

When choosing an entry (enter the number and press ENTER) from one of the two menus, the app navigates to the chosen directory path. If entering ',' before the number, the parent directory of the folder contained within the entry is visited instead.

The history menu (more precisely the most visited directories section) and favorites are sorted alphabetically by directory name for easy identification of the required entry. The recent history section is displayed in a stack-like mode, namely the most recently visited directory is on the first position (see also section 6.1).

If an entry is not found within menu, one can enter the target path manually in order to navigate to the directory. It is not required to exit the history/favorites menu in order to do this. Any input other than the given range of numbers or special options like the quit character (!) is considered regular navigation input. I call this the "input forwarding feature". This feature is present in other menus too.

It is possible to navigate to a specific favorites entry without displaying the list of preferred directories. This can be done by entering operator > followed by the entry number (while on main navigation page or in another menu). For example, if directory /home/myUserName/Documents is entry number 2 in Favorites, then the user can enter >2 and hit the return key to visit it. If the string after the operator is not a valid entry number (which needs to be a positive integer between 1 and the number of favorite paths inclusively), then an error will be triggered.

The same rapid access mode can also be obtained with navigation history (by entering < followed by entry number), yet in this case the quick history needs to be enabled beforehand. Same as for favorite directories, if the entry number is invalid (either not in range or containing invalid characters) an error will be triggered. For more details, please check the quick history section (6.6).

Note: due to its easy reachability, the user home directory is excluded from any history tracking (adding to favorites is also not allowed - an error is triggered when attempting this). This is in order to make most effective use of history entries, especially in quick history (see section 6.6 for more details).

5.3. Special options for visiting directories

5.3.1. Visiting the previous directory

Enter the comma character (,) and press ENTER. You can run this function as many times as you wish. The system will toggle between the two directories.

Note: when first entering navigation mode, the previous directory is the same with the current directory. This is the directory from which the Python script is being executed.

5.3.2. Visiting an ancestor directory

From the navigation menu enter the ; character followed by a positive integer representing the depth (relative to current folder) at which the chosen ancestor directory is located. For instance, the user can switch to the grandparent directory by entering ;2 (which is equivalent to entering ../.. as relative path).

A concrete example would be:
- current directory is /home/MyUserName/Documents/Utils/Recent
- the user enters ;3 in the navigation menu
- new current directory becomes /home/MyUserName

Notes:
- if the provided depth is larger than the number of current directory ancestors (including root), then the maximum depth is considered and the user switches to root directory. In the above example, entering ;5 would be the same as entering ;6 or ;1000 (the user navigates to /)
- the user needs to enter a positive integer after ; (otherwise an error message is displayed and the current directory remains unchanged). Neither non-digit characters, negative numbers or number 0 are accepted. Entering nothing after ; is invalid as well. Trailing spaces are ignored.

5.4. Adding a directory to favorites

From navigation mode go to the directory you need to add to favorites. Then simply enter +> and press RETURN. The current directory is automatically added to favorites (unless it is already a favorite directory in which case a warning message is issued).

5.5. Removing a directory from favorites

From navigation mode enter -> and press RETURN. A menu will be opened. Choose the entry number of the directory to be removed from favorites.

5.6. Executing commands

It is possible to execute regular shell commands (like cd, ls, etc.) or other scripts from the application.

In order to do this you just need to enter the : character followed by the actual command and press ENTER. For example in order to execute 'ls -l' enter ':ls -l'. It is possible to use an alias as well (for more details please check section 5.17).

To repeat the last executed command just enter the :- characters and press ENTER.

To enter a new command by editing the previously executed one just enter : and press ENTER.

It is also possible to enter the command history menu by typing :< and pressing ENTER. Similar to navigation history, by entering a valid number the chosen command is executed.

Same as for navigation history, the commands history has two sections: recently executed commands and most executed commands. The most executed commands are sorted alphabetically, while the recent commands are stacked (see section 6.1).

The command history can also be accessed in edit mode by entering :: and pressing ENTER. In edit mode, when the number of a command is entered the string of the command is displayed for editing. After editing and pressing ENTER, the new command will be executed. If input hasn't been acknowledged by pressing ENTER, the command execution can be aborted by entering : at the end of the string and then pressing the RETURN key.

Last but not least, commands can also be accessed by entering a quick history entry number when on main navigation page. More details in section 6.6.

Important note: in navigation mode make sure you launch time consuming commands in the background by using the ampersand (&) unless you need to visualize the output of the executed command on screen in real time.

5.7. The clipboard functionality

It is possible to move or copy files and/or directories from a directory (source) to another (destination) by using this functionality. This is similar to using cut/copy paste in a GUI environment. In order to do this you need to perform following steps:
- from source directory enter :m (for moving) or :c (for copying) and hit ENTER
- enter a keyword that describes the items to be moved or copied. Press ENTER once done. The keyword should be entered exactly the same as when executing a BASH mv or cp command (wildcards are obviously accepted)
- go to the destination directory
- enter :y (yank) and hit ENTER for having the items moved or copied into the directory

Notes:
1) The source and destination directories SHOULD be different.
2) A keyword that doesn't describe any item will cause a shell error which will trigger a clipboard erase.
3) If items are successfully copied, the clipboard is kept intact, meaning these can be copied again into another folder. This is different from moving, where the clipboard is being erased after executing the move action (:y), whether successful or not.
4) The clipboard is not persistent. It is erased when the script is exited.
5) Any newly initiated move (:m) or copy(:c) operation overrides the clipboard.
6) Use :dc to display the clipboard content and :ec to erase clipboard (the clipboard content is also displayed on the main navigation page).

All relevant clipboard commmands can be found in the clipboard help menu. Type ?clip and hit ENTER to have this menu displayed. The menu does not need to be exited, just continue to enter the desired input in the app.

5.8. Recursive move/copy

It is also possible to move or copy files recursively from one/more source folder(s) to a setup destination (target) directory. In order to do this following steps should be performed:
- Go to the destination directory, enter :td and hit ENTER to have it setup as target. Alternatively you can enter the navigation history or favorites menus and set:
  - entry dir as target dir by preceding the entry number with character '+' and hitting ENTER
  - parent dir of entry dir as target by preceding the entry number with character '-' and hitting ENTER
- Go to the directory you need to move/copy files from and hit :M or :C (case sensitive) to enter the recursive move/copy mode.
- For each item or group of items you require to transfer enter an appropriate keyword and hit ENTER. After transfer is done a new keyword will be requested for the next item or group.
- After entering all keywords and transfering all required items, instead of entering a new keyword just hit ENTER to exit the recursive mode.
- If other files from another folder need to be transferred to the target directory, go to the next source directory and re-enter the recursive move/copy mode.
- Repeat the above steps until all required files from all source directories have been transferred to the destination (target) directory.

Notes:
1) To switch from recursive move mode to recursive copy mode (or vice-versa) you need to exit the current mode (hit ENTER without keyword) and enter the other one by using the appropriate option (either :C or :M).
2) The target directory is not persistent. It is reset at script exit.
3) To reset the target directory, just enter :etd and hit ENTER. Setting up a new dir will then be required for initiating new recursive operations.
4) To display the target directory (if any), enter :dtd and hit ENTER. If the directory is invalid (e.g. has been erased/moved in the meantime) you will be prompted to setup a new one. The target dir is also visible in the main navigation menu.
5) To setup a new target directory just (re-)enter :td and hit ENTER. If a target dir is already in place, it will get overridden by the new target folder.
6) If the target directory is chosen from the navigation menu and the folder no longer exists, then the missing directory case is handled as follows:
   - for the missing directory contained within menu entry the same steps are required as when visiting the directory through the menu. For more details regarding missing directories from menu check section 5.14.
   - if the parent was chosen as target dir and it no longer exists, a warning message will be shown and the target dir is not setup. No further actions are enforced from menu.

All relevant recursive move/copy commmands can be found in the clipboard help menu. Type ?clip and hit ENTER to have this menu displayed.

5.9. Getting help

The main application options can be viewed by entering the ? character and hitting ENTER. The application remains in "default mode" meaning the user can continue to use the navigation and commands functionality without the need to exit the help menu.

This main help menu is complemented by two specialized ones, namely the clipboard/recursive help (type ?clip and hit ENTER) and the batch renaming help menu (?ren + ENTER). For more details about these functionality areas please check sections 5.7, 5.8 and 5.13.

5.10. Settings

For specific functionality domains settings files have been created. These have names ending with _settings.py. The settings files contain specific variables that can be modified by user for doing adjustments in the behavior of the application. Examples of possible changes are:
- changing the minimum number of characters a command should have so it gets stored within commands history
- changing the names and location of the history files (they are all located in the user home directory as per default settings)

Currently settings are available for:
- navigation (navigation_settings.py)
- commands (commands_settings.py)
- batch renaming of files contained in the current directory (rename_settings.py)
- application-level setup (system_settings.py)

For more details please consult these files and read the comment added to each settings variable.

5.11. Toggling between menus

When the user is in one of the following menus it is possible to toggle to its "counterpart" menu:
- navigation history -> to navigation favorites
- navigation favorites -> to navigation history
- commands history execute mode -> to edit mode
- commands history edit mode -> to execute mode

The user just has to enter option :t while in one of these menus and hit ENTER.

Please note that no toggling occurs if the counterpart menu has no entries available. Instead the same error message is displayed as if the user tried to enter this menu from the start.

To be noted is that the toggle option works in filtered menus as well. The counterpart will have the same filter applied. Same rule applies here: if the counterpart does not have any entries, when applying that filter then no toggling will occur and the corresponding error message is displayed.

If the user enters the toggle option without being in either of the above menus, then a distinct error is displayed stating toggling is not possible.

The toggle option is particularly useful in filtered menus (see section 6.5) by saving the effort of manually re-entering the filter for the menu counterpart (most commonly when the user wants to edit a command instead of directly executing it).

Note: by re-entering option :t the user toggles back to previous menu (and so on...). This back-and-forth toggling is obviously not applicable if the counterpart menu has no available entries.

5.12. Re-entering the last used filter

For more details regarding filtered history please consult section 6.5.

If a filter has been previously input for navigation/commands, it can be re-entered by using a (short) specific keyword without the user requiring to re-enter the actual filter keyword. The last entered filter keyword is displayed on the main navigation page, namely:
- last used navigation filter
- last used commands filter

Following specific keywords can be entered to apply the last used filter:
- :n for applying the last used navigation filter to the navigation history
- :N for applying the last used navigation filter to the favorites
- :f for applying the last used commands filter to commands history in execute mode
- :F for applying the last used commands filter to commands history in edit mode

Notes:
- the filter might yield no results (same as when applying it directly by entering the filter keyword)
- if no filter has been previously entered, then an error message is displayed and no filtering is performed
- the filter is displayed on the main page exactly as previously input by user from keyboard. This means it might for example contain preceding and/or trailing whitespaces. This is not the case with the filter displayed in the filtered navigation/commands menu (a.k.a. "applied filter". This one is actually the "pre-processed" filter which was used to perform the concrete filtering. The ones displayed on the main navigation page could be called "raw filters", as they represent the user "raw" input.

5.13. Renaming a batch of items

It is possible to rename all items from the current directory by using various schemes. Please note that for safety reasons the items that are hidden are excluded from this functionality.

Batch renaming involves two basic operations: adding substrings and removing substrings to/from each item name. This can be done in more ways which will be presented below.

The adding of the substring can be done:
- either by adding a fixed string (like "Photo_") to each item. For example FileA becomes Photo_FileA, FileB becomes Photo_FileB and so on.
- or by adding a number that is then incremented for each item. For example FileA becomes FileA1, FileB becomes FileB2 and so on.

Following renaming schemes are currently supported:
- appending a fixed string to each item name
- appending a number that is incremented for each item
- prepending a fixed string
- prepending a number
- inserting a string by specifying the index within the item name where the insert should occur. For example if the item is FileA, the index is 1 and the string is "_cc_" the resulting name will be: F_cc_ileA
- inserting an incrementable number
- deleting a substring from each file. For example if deleting 2 characters at index 1, FileA becomes FeA and FileB becomes FeB.
- replacing a substring with another substring. In addition to file index the number of removed characters should also be given. For example, if the file is FileB, the index is 1, the number of removed characters is 2 and the substring to be added is _dd_ the resulting filename is F_dd_eB
- replacing a substring with an incrementable number

It is possible to combine these operations for more complex renaming. However this has to be done in separate sessions, as the functionality does not allow executing them "on the fly". Actually I wouldn't even recommend this. In my opinion it is better to check the intermediary results each time an "atomic" operation is performed.

For details regarding the commands to be used please check the renaming help by typing ?ren in the navigation menu and hitting ENTER. For example the command for appending a fixed substring to each item is :ra.

The steps for performing the renaming are as follows:
- navigate to the directory in which the items should be renamed
- execute the option of the chosen renaming scheme
- an interactive menu is displayed where the user is prompted to provide all required data
- after entering this data, a simulation of the renaming is performed and some before/after examples are displayed. Hit y (yes) or n (no) and press ENTER to perform the actual operation or abort it.

Notes:
1) In the interactive menu, prior to reaching simulation it is anytime possible to abort renaming by just hitting RETURN provided no input has been entered.
2) For renaming by using an incrementing number, it is required to mention the starting value in the interactive menu. For example if the initial value is 3 FileA will be renamed FileA3, FileB - FileB4 and so on when choosing append mode.
3) Only valid input parameters are accepted. For example it is not allowed to enter negative indexes for insertion. You will be required to re-enter the param if it is not valid.
4) The system performs some checks based on the entered parameters. The renaming operation will NOT be allowed if any of following conditions occur:
   - duplicates would result from renaming. If for example you remove one character at index 4 from FileA and FileB the resulting names would be File. This would cause the overriding of the content of one of the files by the other. Such an issue might cause a severe data loss.
   - at least one of the items cannot be renamed due to parameters that are not fit for its original name size. For example if 2 characters were required to be removed at index 5 of FileA, this operation would not be valid for the simple reason that there is nothing to remove at this index. Even if the other items are eligible (say FileAbcdefgh), the operation is still not allowed because each visible item needs to be renamed.
   - also if no visible items are present in the current directory an error will be triggered prior to entering the interactive menu.
5) As all visible items from the current directory are included in the renaming process, the user should decide whether it is required to rename all of them or not. If not, the excluded items should be moved to a separate directory that is NOT a subdir of the current folder.

5.14. Handling missing directories

It can happen that for an entry chosen from navigation history or favorites the path doesn't exist anymore. This can happen for various reasons:
- the directory has been deleted
- the directory has been moved, renamed or a combination of both

In this case the user has two options:
- remove the entry from the menus
- remap the path to an existing one (for example when the directory has been renamed) in order to preserve the number of visits

Note: this functionality is NOT available when choosing the parent dir from the entry. In this case only a warning message will be displayed asking to remove/map the entry. Generally speaking the actual removal/mapping is triggered when individually selecting each directory (not parent) from the navigation menu (history/favorites).

5.14.1. Removing the path

When this option is chosen, the path is removed from all menus. The number of visits is lost.

5.14.2. Remapping

The user might opt for replacing an invalid path from the navigation menus (history/favorites) with another path. The replacing path might be:
- one that already exists withing menus
- one that is contained in navigation history but doesn't have enough visits (or hasn't been recently visited) to be included in the consolidated history menu
- a path that hasn't been visited since the last history reset and is not a favorite path either

Depending on the above mentioned conditions following scenarios are available:
- an unvisited path will replace the invalid path in the menu; it will take the number of visits of the replaced path (please note the the position might not necessarily be the same as a re-sorting is performed)
- a path with not enough visits or not visited recently enough will show up in consolidated history with the same number of visits that the invalid path had
- a replacing path that is already contained in one of the menus will remain in that menu but the number of visits will be updated if the invalid path had more of them

In either case the invalid path is completely removed from all menus.

It is possible to easily choose the replacing path from history/favorites by entering '<' or '>' and hitting ENTER when the user is prompted to enter a replacing path. The user will be brought to the chosen menu from which he can choose one of the paths by entering its number and hitting ENTER. If no path is suitable then the user still has the possibility to enter another path manually without exiting the chosen menu.

It is not possible to switch between history and favorites menus when choosing the replacing path. The user must first quit the re-mapping process by hitting '!' + ENTER and then restart re-mapping by choosing the invalid path from menus again.

Also when choosing a valid replacing path the current directory will be switched to this path after remapping.

Note: the home directory cannot be used as a replacing path in the remapping process. This is because it is excluded from any history tracking (see note from section 5.2).

5.15. Adding commands to history based on command string size

It is possible to setup the minimum number of characters a command should contain in order to be stored within commands history. This is done by setting up the min_command_size variable in commands_settings.py. For example, by setting min_command_size=10 each command with less than 10 characters will be prevented from being included into the command history. The count does not include the : character used for entering the command in navigation mode. This rule can be bypassed by setting the minimum number of characters to 0 in the settings file.

Note: this setting does not affect storing the command in the "last executed command" buffer, which is updated each time a command is executed no matter how many chars the command contains. The content of this buffer is volatile and is erased once exiting the goto_app.py script.

5.16. Sensitive commands

It is possible to mark specific commands as sensitive. This is done by manually modifying the value of the sensitive_commands_keywords variable in commands_settings.py by adding a search keyword to the set. For instance, if the keyword is 'rm ', every command containing this string will be marked as sensitive. The space is important, as it would not be desired that any command containing this substring (like 'echo permanent' to be added to the sensitive area. This functionality is useful for preventing accidental execution of commands that produce irreversible unwanted results. Examples of such commands are: rm, rmdir, mv.

How this actually works:
- if the user launches a command into execution, the script will check whether the command string contains one of the substrings that had been added to sensitive_commands_keywords
- if the command contains (at least) one of these substrings, a prompt will be displayed asking the user to confirm the command execution
- the user should enter y (yes) for confirming and n (no) for declining. The option is case insensitive but should be one of these two.
- if the operation is confirmed, the command will get executed, otherwise it will be cancelled

Note: the functionality is active whenever a command is being launched to execute. This includes:
- entering a new command (command string preceeded  by ':') and hitting ENTER
- launching a command from (filtered) commands history menu in execute mode by choosing one of the menu entries
- editing an existing command (from (filtered) commands history menu or the previous command) and launching it by hitting ENTER
- repeating the previous command without modifying it (option :-)

I strongly recommend using this functionality by extending and refining the list of sensitive keywords and carefully checking the command and current directory prior to choosing the 'y' option. The principle "better safe than sorry" has a good application in this situation.

5.17. Command aliases

Even if this script has a command history functionality, in some situations it might be more efficient to use an alias as a shorthand for a specific command. For this purpose, the alias functionality has been created as a built-in feature of this application. It resembles the aliases supported by the UNIX shell, however compared to them it has some limitations. For example the alias keyword can only be used at the beginning of a command.

The aliases implemented in this app work as follows:
- the application reads the command string
- the substring until the first encountered space is checked against the keys from an aliases dictionary
- if a match is found, then it is substituted with the corresponding value (alias content) from the dictionary
- the resulting expanded command is launched into execution

A simple example would be a shell command that counts the number of files/subdirs from the current directory. The command is: ls -l | wc -l. For the first part, an alias ll=ls -l might be used, which means the user would enter: ll | wc -l. When entering the "aliased" command (ll | wc -l), the application searches the dictionary, expands the command by replacing ll with ls -l and subsequently executes the resulting string. The only requirement is that the user previously "registered" this alias, otherwise no expansion can be performed. The command would be executed exactly as entered resulting in a shell error (there is no ll command in the UNIX shell). For more details regarding alias registration see next subsection.

Notes:
- regarding above example, it is currently not possible to use an alias for wc -l in the same time, i.e. ll | wl, where wl is an alias for wc -l. This might get supported in future app update. Instead an alias could be employed for the whole expression, for example alias ic ("items count"): ic=ls -l | wc -l.
- it is not supported to use an alias which expands to a string containing other aliases. The reason is that the expansion of the command is not performed recursively but only for the first keyword. An example of recursive aliasing would be having an alias ll for 'ls -l' and an alias ic with content 'll | wc -l'.

5.17.1. Registering an alias

In order to use an alias within a command, it is required to have it first registered, i.e. stored in the aliases dictionary. Actually this map is loaded from/saved to a JSON file which resides in the user home directory (more details below). The application provides support for entering, modifying or removing one or more aliases in a single interactive session.

Enter :a and press ENTER in order to access the aliases maintenance menu. An interactive "loop" is opened, where the user is first asked to enter the alias and then the content (expansion). For example, the 'll' can be entered as alias followed by content 'ls -l'. Then another alias and corresponding content is being asked for and so on.

The menu enables three operations:
- entering a new alias that is not contained within dictionary/JSON: the alias and content should be entered as already mentioned above
- modifying the content of an existing alias: the alias should be entered followed by the new content which subsequently overrides the old one
- deleting an alias: the alias should be entered and when entering the content the user should just press ENTER

After finishing the data entry process, the user should directly press ENTER when asked to enter a new alias. A prompt with the performed changes asking the user to acknowledge them is being displayed. The user should enter 'y' (yes) to save the changes or 'n' to cancel them. If the changes are cancelled, they are lost and the user should resume the process in case adding/modifying/deleting aliases is required.

To be noted:
- a JSON file (.aliases.json) located within user home directory is being employed for storing all aliases and for loading them when the script is launched. When entering the interactive menu, the aliases JSON file would be automatically reloaded if it was previously modified by another script session. The JSON file is named as a hidden item in order to prevent manual changes. It is recommended to update it exclusively via app by using the already mentioned maintenance menu.
- while in maintenance menu, each change performed on an alias overrides the previous one. For example if the user entered alias rmd=rm -r and then alias rmd=rmdir, then the last change is the one to be applied. This includes cancelling entering a new alias by entering it again and hitting ENTER for its content. On the reverse side the user can also cancel a removal by re-entering the alias with the same previous content or a modified one. To be on the safe side, the user should carefully check the list of changes before acknowledging them with the 'y' option.
- the alias string should be valid, meaning it should only contain alphanumeric characters. Any other characters are considered illegal and the application will trigger a warning. Also, please note that any alias string is automatically converted into lower case.
- the saved changes are available to other script sessions that are opened AFTER performing the aliases save operation. Unlike history files, it is not necessary to close the current session in order to trigger saving to the aliases file (instead this is done by closing the maintenance menu and acknowledging the changes). If other sessions are already open when the changes take place, the aliases list will be refreshed when entering the interactive menu (:a) or the read-only menu (see next section). The entered/modified aliases would then be usable for entering commands.
- it is advisable not to use aliases that are identical to shell command keywords (e.g. rm, rmdir etc)
- the user should also avoid using aliases that are identical to special options used in the application. An example would be using "ra" as alias, which is identical to the rename-append option belonging to the items batch renaming functionality (see section 5.13 for more details). These aliases might not be usable as they might get "shadowed" by the special options.
- it is not possible to remove all aliases. They can only be deleted one by one in the maintenance session.

5.17.2. Checking existing aliases

Enter option :A followed by the ENTER key. A list of existing aliases and corresponding expansions is being displayed. Either of these aliases can be used as a shorthand for entering a preferred command. The list is information-only, meaning there are no shortcuts for accessing a specific alias or for modifying it. Any modification should be performed via interactive (maintenance) menu (enter :a + ENTER - see previous section).

Note: if the JSON file was modified by another script session, it would automatically be reloaded before displaying the list of available aliases.

5.17.3. Entering a command with an alias

The command can be entered as any other command with the caveat that the alias should be the starting keyword. The entered string should therefore have following format:
:[alias] [remaing command options/arguments]

An example would be entering :emacs myFile.txt on MacOS. In this case "emacs" would be used as an alias for 'open -a emacs'. Using this alias also ensures "compatibility" with Linux systems, where the open command with option -a is not being required for opening an application. The user can then have a seamless back-and-forth transition between these OS-es.

6. THE HISTORY FUNCTIONALITY

Each time a directory is visited or a command is executed, the event is tracked in a history file. There are three different history sections available:
- recent history
- persistent history
- excluded history (navigation only)

The command history only tracks the shell commands executed within the app, namely the ones preceded by the : character. It is completely separate from standard terminal (shell) history which tracks commands executed directly within terminal ("bare metal" commands).

6.1. Recent history

Most recently visited directory paths or executed commands are stored here. It has a limited number of entries (which is specified by a variable from navigation_settings.py / commands_settings.py) and older content is continually overridden.

The entries are stored "in order" but duplicates are not allowed. A circular buffer behavior is implemented instead: if the maximum number of entries is reached, the least recently visited path/executed command will be taken out. Unlike persistent history (see next section), the entries are NOT displayed to the user in a sorted fashion. Instead they are shown in reverse order of their access, i.e. first entry is the last visited directory or executed command.

A subset of the recent history is the quick history, see section 6.6.

6.2. Persistent history

For navigation, all paths except the ones from excluded history are mentioned here along with the number of visits. When a new directory is visited the first time on the current day the number of visits is incremented. Further visits on the same day are not taken into account. This prevents unrealistic reporting which might occur if a directory has been entered many times during a day and then remains unvisited for a long time.

Also if the previous directory is the same with the visited directory the persistent history is not updated.

The persistent history is sorted each time it is updated and the most visited paths are added to a consolidated history menu.

The same persistent history behavior is implemented for executed commands. No excluded history is available here.

The persistent history holds an unlimited number of entries. However only a limited number (specified by a variable from navigation_settings.py / commands_settings.py) is displayed in the unified menu (consolidated history), namely the ones that have been visited/executed the highest number of times.

6.3. Consolidated history

This a unified menu that consolidates the entries contained within:
- recent history (all entries are added to consolidated history)
- persistent history (most visited entries are added to consolidated history, see previous section for details).

6.4. Excluded history

When a directory is added to favorites, its entry from persistent history is moved to the excluded section. This way the number of visits continues to be tracked (same tracking mechanism as for persistent history) and in the same time the path is separated from consolidated history.

When the directory is removed from favorites, the entry is moved back to persistent history with the actual number of visits. The consolidated history is updated accordingly.

There is no excluded history for commands.

6.5. Filtered history

Both for visited directories and executed commands it is possible to filter the persistent history (whole content) based on a search keyword. The search will find all matches but only display a limited number of results on screen. This limitation is implemented so the displayed entries are readable and thus usable. By modifying a variable in the navigation_settings.py or commands_settings.py it is possible to change this limit (however I recommend keeping it low).

Once the search results are displayed, please select the number of the required entry from the menu so it is executed/visited. The filtered history menus behave the same as the consolidated menus regarding usage (for example for navigation one can enter ',' before the entry number in order to visit the parent directory of the entry).

The same filtering mechanism also applies to favorite directories.

To filter visited paths enter << followed by the search keywoard and hit ENTER. For example enter <<abcd to find the directory '/home/user_a/abcdefgh.'

To filter favorite paths enter >> followed by the search keyword and hit the ENTER key.

To filter executed commands enter:
- :< followed by keyword to display filtered entries so one is selected for executing. Example: type :<abc to search for 'echo zabcd' (exec). Choosing the entry will launch the command into execution.
- :: followed by keyword to display filtered entries so one is selected for prior editing before executing. Example: type ::adg to search for 'echo zadgb' (edit and exec). Choosing the entry will make the command available for editing before it is launched into execution.

In the above examples the search keyword contains a single filter. However both for visited paths and executed commands it is possible to use multiple filters in order to refine the search. These should be separated by commas, i.e. keyword should have the format: [filter_1],[filter_2],...,[filter_n]. Each keyword filter is being used for conducting a separate search. Search results are AND-ed. For example if the user enters <<abc, def then results matching 'abc' AND 'def' are being displayed. Note that for each filter the preceding and trailing whitespaces are being ignored (for example when entering :<    abc, def the filters are 'abc' and 'def'). Only spaces contained within filter are being taken into consideration, e.g. <<abc, d ef implies using 'abc' and 'd ef' as filters. This is especially useful for finding commands as these might also contain spaces.

Last but not least each individual filter is counted as a regular expression so the specific regex syntax can be used. However this should be valid, otherwise no search results will be returned. For example entering ::* will yield no results.

Notes:
- all persistent history entries (including the ones not displayed in the consolidated menu) are being searched for the given keyword. This gives the user a chance to reuse the less visited/executed paths/commands as well.
- the search is case-insensitive, meaning you can enter <<abcd for /home/aBcd retrieval
- the number of spaces within search keyword filter is relevant and should be the right one for identifying the substring in the command/path. For example you should enter :<cho ab and not :<cho  ab to find the echo abdcgijk command. As already mentioned before, preceding and trailing spaces are ignored for each filter.
- if the number of found entries is higher than the displayed ones try to narrow down the search if the required path/command is not visible. This can be done by modifying the filter(s) within keyword or by adding new filters separated by comma. Feel free to use regex specific syntax as well if required.
- also if no match was found try to modify the search keyword until getting the desired result. If the result is still not obtained it is likely that the required entry is not contained within persistent history
- the excluded history is not contained in the paths used as navigation history filtering base (<<). This is because the navigation history search is performed only in the persistent history entries. It is possible to filter excluded history separately by using prefix >> (favorite paths filtering)
- empty filters are ignored. For example if the user enters <<,,abc only abc is being used for the search. If no non-empty filters were entered, then no results would be displayed. Please note that filters containing only whitespaces are also considered empty.
- it is also possible to search for entries that DON'T contain a specific keyword (complementary). In order to do this without using specific regular expression, the user could enter the keyword preceded by the '-' character. This is the same (yet much easier) as writing ^((?!keyword).)*$ which would be rather messy. For example by entering dir1, -dir2 (or vice-versa) the entries that contain dir1 but not dir2 are being searched for. Say there are two distinct directories, namely /home/user1/dir1 and /home/user1/dir2/dir1. By using the mentioned filters combination, only the first entry would be displayed. This is particularly useful when two (or more) similar directory structures with different base directories exist and the user is interested in navigating in only one of them. Same can be used for similar commands, e.g. two shell commands that differ by only one option.
- the keyword search without using '-' is actually a regex match, as each keyword is a regular expression construct. When using the '-' character, the keyword is expanded into the valid regex mentioned in previous note

6.6. Quick history

The quick history is a subset of the recent history. It is available both for navigation and commands and is displayed as a unified menu within main navigation context.

The quick history navigation section contains the last visited directories. The number of displayed entries cannot exceed the size of the recent history (instead it can be smaller resulting in a subset). It is recommended to keep the count as small as possible in order to be able to identify the required entry rapidly (hence quick history) and then navigate to the directory.

The navigation to the chosen entry is performed by entering < followed by entry number. Please note that the number should be valid, i.e. it needs to be a valid integer pointing to one of the listed entries. If the entry number is out-of-range or contains invalid (non-numeric) characters, then an error will be triggered. The user should correct the input and retry.

The quick history might also contain a commands section if a recent commands history is available. To access a command, enter character '-' followed by the entry number. This will trigger the execution of the chosen command. In order to edit it prior to executing, enter character '+' followed by entry number instead. Same rules as for navigation apply regarding entry number validity.

By default the quick history is disabled, so it doesn't clutter the main menu unnecessarily. To enable it, enter option :q from main navigation page or another menu. To disable it, enter the same option again. Please note that the quick history is persistent during the entire session unless disabled. It goes off when exiting the script.

Another caveat is that the quick history can only be used from the places where it is being displayed, namely the main navigation page (a.k.a. main menu / main context). Although the help sub-menus are also part of the main context, they are excluded from using this feature. When accessing either of the help options, the quick history is automatically disabled. The user can re-enable it by entering :q (help information is being cleared when doing this).

If the user attempts to access a quick entry from another context (e.g. enters <2 while in the filtered navigation history menu), then an error is triggered mentioning that the context is not appropriate. The context is automatically switched to main navigation page, and the user can re-enter the quick navigation choice. This time the navigation/command should be successful unless the quick history is disabled or the entry is invalid. The reason for implementing this menu(context)-based restriction is that it needs to be ensured the user is fully aware of the chosen entry before executing it. This is of utmost importance especially when executing commands.

Last but not least, when using the navigation section of the quick menu, it is also possible to visit the parent directory of the chosen entry. To do this, instead of < enter ,, followed by entry number. For example, if directory /home/myUserName/Documents is displayed at position 2 in quick navigation history, then simply enter ,,2 in order to visit its parent /home/myUserName. All above mentioned quick history rules apply here.

Notes:
- to modify the number of displayed entries, please change the variable q_hist_max_entries from navigation_settings.py (for navigation) or commands_settings.py (for commands) to the desired value (default is 5 and it is recommended to keep it small).
- when accessing the parent directory, an empty entry number (namely entering only ,,) is considered invalid and an error is triggered. The user should retry by entering a valid entry number.
- the quick history cannot be accessed when both the navigation and commands history are empty. Also, if both consolidated history menus are emptied while quick history is enabled, then it gets automatically disabled. It can be re-enabled as soon as at least one directory is visited and/or at least one command that has at least as many characters as contained within setup threshold (see section 5.15 for more details) is executed.

7. FALLBACK FOR CURRENT DIRECTORY

In rare situations, the current directory might become unavailable. This might happen for example when it has been deleted externally (e.g. by using a separate terminal) or when the permissions have been altered.

When this is the case, the application uses a fallback mechanism that replaces the current dir with a preset fallback directory. It is highly recommended to use the home dir as fallback, yet if you would like to use another folder this can be setup in system_settings.py. However you should make sure the fallback dir is valid and accessible at any time.

The fallback mechanism works as follows: when the user tries to execute an operation (e.g. go to another folder) the application performs a sync process. First it is being checked that the current directory is reachable. Then if the current dir is available it continues the operation as per normal process. However if the current dir is not reachable anymore, the app changes it to the fallback directory and warns the user that the requested operation could not be performed. The user can try again afterwards or choose to execute another operation by taking the current directory change into account.

To be noted:
- the clipboard and recursive transfer operations are reset at fallback meaning the user will need to re-initiate these processes (with new parameters if required)
- entering the help menus and exiting the application is still possible at any time. In these situations a "silent fallback" is performed. This process is made known to the user by displaying the "(fallback)" keyword along with the path of the current directory.
- on MacOS if Finder synchronization is enabled, when a fallback is performed the sync is preserved and the Finder opens in the fallback directory

The fallback mechanism has been designed for increasing the resiliency of the application by aiding in preventing unwanted crashes. Due to the complexity of the application, there might be some places (sub-menus) where it hasn't been implemented (in this case the app might crash), yet in practice it should be seldom required as in most of the situations the current directory should be fully available.

8. DATA RECONCILING

The application does not modify its history files at runtime, meaning all operations occur in-memory. This was implemented in order to fully support running multiple sessions in the same time. When the script gets launched, it starts by loading all relevant content from the application files into the required data structures. These structures are then updated during runtime as the user navigates through directories and/or executes shell commands. Finally, when the user decides to exit the application, the content of these data structures is written back to the history files, which fully overrides them.

Three JSON files are currently used for history tracking:
- .navigation_history.json (recent history / persistent history / daily log for visited directories)
- .commands_history.json (recent history / persistent history / daily log for executed commands)
- .excluded_navigation_history.json (history tracking for favorite directories)

An issue might arise when at least two script sessions are active. Each session performs its own operations without being aware of the other process. At some moment in time the user might decide to close one of the sessions, which triggers saving the data to the application files. These files are obviously shared by all script sessions. Later when the other session gets closed, it will override the files again. As the sessions are unaware of each other, this would pose the risk that the changes performed by the previously closed process are lost.

In order to prevent this and to preserve consistency of the operations, a data reconciliation mechanism has been implemented. When a session gets closed, it is first being checked whether another session modified the files while the current one was active. If this was the case, then the files would be reloaded into separate in-memory data structures. Both data groups (from previous/current session) are then analyzed against each other, reconciled and consolidated into a single unified group of data structures. The consolidated structures (reconciled data) are then saved to the application files.

The reconciliation process ensures that:
- paths removed from persistent/excluded history by a script session (e.g. directories that no longer exist) stay removed and don't get written back to the application data files (unless the other session reverted these changes, i.e. recreated the erased directory)
- the number of times a specific path was visited, respectively a command was executed is the right one (e.g. a directory visited during previous session but not visited in current session will have the updated number of visits)
- when a path has been added to/removed from favorites by one of the sessions, it stays added/removed unless the other session has performed its own modifications on it
- newly visited paths/executed commands are contained within history
- newly visited paths are visible in favorites if added here by one of the sessions

Notes:
- the recent navigation/commands history is always the one from the last closed session, it overrides the ones from previous sessions.
- the aliases JSON file is not subject to data reconciliation. The changes are being saved as per user request during the session in which they have been performed. More details in section 5.17.

To conclude, the goal of reconciling data from multiple sessions is to obtain a clean persistent/excluded history by ensuring the right entries with the right number of visits/executions are present within these files after closing all sessions.

9. MISCELLANEOUS

1) It is possible to erase all entries from history, which means all history data is erased. When this happens, there are no more entries in the consolidated history menu and viewing that menu is disabled (a warning will be issued by script). However the navigation favorites menu retains its entries, yet the number of visits mentioned in excluded history is 0. Type :clearnavigation and hit ENTER in order to clear the navigation history. For command history type :clearcommands and hit ENTER. In each case, the user will be prompted to confirm the clear operation. Type y + ENTER to confirm or n + ENTER to abort.

2) When exiting the Python script (either by entering ! or CTRL+C / CTRL+D), the current directory is not retained but the terminal will revert to the original directory that was current when launching goto_app.py.

3) When using CTRL+C or CTRL+D from the clipboard, recursive transfer or rename menus, the user returns to the main navigation page and any operation related to these menus is aborted. When hitting these key combinations in any other menu or dialog the application is exited. Please note that CTRL + D might not always work (in some situations it might not have any effect).
