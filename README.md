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

2. SUPPORTED OPERATING SYSTEMS

The script is supported both on Linux and MacOS. It is not supported on Windows.

The pre-requisites for running it correctly are:
- Python 3.6 (minimum version)
- BASH CLI

On MacOS the Anaconda navigator should be installed in order to ensure the script works properly.

Following should be noted for each supported OS:

1) On the Linux version the "CLI-only" mode is supported. This means the script does not synchronize the current directory of the terminal with the one from the explorer window. The reason for this implementation is that there are several distributions of Linux and the explorer tool might be differ from one to another.

Unlike the non-Python (BASH-only) version of the script it is NOT possible to obtain synchronization between terminal and graphical explorer if the terminal is embedded in an explorer window (as on OpenSUSE). This is due to the fact that the script runs in a sub-shell of the terminal. If you require this synchronization please use the BASH-only scripts (see section 8. for more details)

2) On the MacOS version the terminal can be synchronized with the Finder window. This occurs as follows: when a valid path is entered in the terminal the Finder will close and the re-open in the directory for which the path has been entered. This occurs no matter if the path is the same with the old one or not and this behavior has been implemented as the user might sometimes need to refresh the Finder window. The possible reason for requiring Finder refresh is mentioned in section 4. By default the sync feature is disabled but it can be enabled by entering :s (+hit ENTER) in the navigation menu. To disable it enter :s again and hit the RETURN key. It is possible to enable synchronization at application startup by setting the finder_sync_enabled setting to True in system_settings.py. Also when closing the application the Finder sync is disabled and the Finder window is closed.

3. INSTALLATION

Use the master or linuxScript branch to download the Linux version and macOsScript branch to download the MacOS version. Clone from the repo, switch to the chosen branch and follow these steps:

a. Ensure you have Python 3 installed (on Mac OS install Anaconda). Check whether /usr/bin/python3 exists. Minimum required Python version is 3.6.
b. Create an alias for /usr/bin/python3 [absolute_path_of_cloned_repo]/goto_app.py in .bashrc. On Mac OS after installing Anaconda it is sufficient to enter keyword python instead of /usr/bin/python3 in the alias.
c. Open a new terminal window/tab and start using the functionality by executing the command alias mentioned at previous point.
d. Before shutting down the machine, in order to prevent forceful terminal closure, exit the script by entering the exit key (character '!') and pressing ENTER. Alternatively the CTRL+C or CTRL+D keyboard combination can be used.

4. KNOWN ISSUES/BUGS

1) Depending on terminal size there might be empty lines between navigation/command history or navigation favorites menu entries. To correct this you just need to resize the terminal until this spaces disappear. In OS-X it is possible to setup a pre-defined terminal size (number of lines/columns) from the Terminal settings.

2) When having directories like ./abcd and ./abcdefgh there are issues when using wildcards. For example if using *ab to switch to either of these two an error will occur and the change dir command will not be executed. A workaround is to type a*d for switching to abcd or a*h for switching to abcdefgh. Also a good practice that I recommend is (as much as possible) not to create a folder that has its name included as first part of the string of another dir.

3) Sometimes when having the Finder re-opened the window is in an inactive state and the user cannot move between directories by using the arrow keys. To correct this initiate a new re-opening in the current directory by entering '.' and pressing ENTER. Also it is possible to use the :s option for disabling terminal syncronisation if you don't necessarily want to see the directory content in Finder.

If any other bugs are discovered please feel free to report them on my Github page: https://github.com/LiviuCP.

5. FUNCTIONALITY

Following features are contained in the script:
- navigation functionality for changing the current directory
- navigation history reporting
- storing directories in a favorites menu
- command executing functionality

To access these functions you need to execute the goto_app.py script. These features will be detailed in the following sections.

5.1. The goto functionality

Enter navigation mode. Then enter the path of the directory to be visited.

You can enter:
- absolute paths
- relative paths
- paths with wildcards

Notes:
1) If no argument is entered the user home directory will be visited.
2) If the same directory as the current one is entered the previous dir will remain unchanged.

5.2. The navigation history and favorites menus

Enter navigation mode, then enter < for history or > for favorites.

The history menu keeps track of the:
- recently visited directories
- most visited directories

The favorites menu contains the directories the user previously added to the list of preferred folders. It is not limited in number of entries, however it's recommended to use it for storing the so called entry-point directories (like Desktop, Pictures, Documents, etc). It can also be used for storing paths to temporarily mounted filesystems (like SD cards). If accessing a temporary filesystem make sure it is mounted before doing any access attempt.

When choosing an entry (enter the number and press ENTER) from one of the two menus, the chosen directory is automatically visited. If entering ',' before the number, the parent directory of the folder contained within the entry is visited.

The history menu (more precisely the most visited directories section) and favorites are sorted alphabetically for easy identification of the required entry. The recent history section is displayed in a stack-like mode, namely the most recently visited directory is on the first position (see also section 6.1).

If you cannot find a entry, simply enter the required path(s) to navigate to the directory you wish to visit. It is not required to exit the history/favorites menu in order to do this. Any input other than the given range of numbers or special options like the quit character (!) is considered regular navigation input. I call this the "input forwarding feature". This feature is present in other menus too.

It is possible to navigate to a specific favorites entry without displaying the list of preferred directories. This can be done by entering operator > followed by the entry number (while on main navigation page or in another menu). For example, if directory /home/myUserName/Documents is entry number 2 in Favorites, then the user can enter >2 and hit the return key to visit it. If the string after the operator is not a valid entry number (which needs to be a positive integer between 1 and the number of favorite paths), then an error will be triggered.

The same rapid access mode can also be obtained with navigation history (by entering < followed by entry number), yet in this case the quick history needs to be enabled. Same as for favorite directories, if the entry number is invalid (either not in range or containing invalid characters) an error will be triggered. For more details, please check the quick history section (6.8).

5.3. Special options for visiting directories

5.3.1. Visiting the previous directory

From the navigation menu enter the comma character (,) and press ENTER in order to achieve this. You can run this function as many times as you wish. The system will toggle between the two directories.

Note: when first entering navigation mode the previous directory is the same with the current directory. This is the directory from which the Python script is being executed.

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

From navigation mode go to the directory you need to add to favorites. Then simply enter +> and press RETURN. Each directory can only be added once to the favorites menu.

5.5. Removing a directory from favorites

From navigation mode enter -> and press RETURN. A menu will be opened. Choose the entry number of the directory to be removed from favorites. Any other input will be handled as normal navigation input by using the "input forwarding feature" that was previously mentioned.

5.6. Executing commands

It is possible to execute regular shell commands (like cd, ls, etc.) or other scripts from the navigation mode. 

In order to do this you just need to enter the : character followed by the actual command and press ENTER. For example in order to execute 'ls -l' enter ':ls -l'.

To repeat the last executed command just enter the :- characters and press ENTER.

To enter a new command by editing the previously executed one just enter : and press ENTER.

It is also possible to enter the command history menu by typing :< and pressing ENTER. Similar to navigation history, by entering a valid number the chosen command is executed.

Same as for navigation history, the commands history has two sections: recently executed commands and most executed commands. The most executed commands are sorted alphabetically, while the recent commands are stacked (see section 6.1).

The command history can also be accessed in edit mode by entering :: and pressing ENTER. In edit mode when the number of a command is entered the string of the command is displayed for editing. After editing and pressing ENTER the new command will be executed. The command execution can be aborted by entering : at the end of the string and pressing ENTER.

Important note: in navigation mode make sure you launch time consuming commands in the background by using the ampersand (&) unless you need to visualize the output of the executed command on the screen.

5.7. The clipboard functionality

It is possible to move or copy files and/or directories from a directory (source) to another (destination) by using this functionality. This is similar to using cut/copy paste in a GUI environment. In order to do this you need to perform following steps:
- from source directory enter :m (for moving) or :c (for copying) and hit ENTER
- enter a keyword that describes the items to be moved or copied. Press ENTER once done. The keyword should be entered exactly the same as when executing a BASH mv or cp command
- go to the destination directory
- enter :y (yank) and hit ENTER for having the items moved or copied into the directory

Notes:
1) The source and destination directories should be different.
2) A keyword that doesn't describe any item will cause a BASH error which will trigger a clipboard erase.
3) If items are successfully copied, the clipboard is kept intact, meaning that these can be copied again into another folder. This is different from moving, when the clipboard is being erased after executing the move action (:y), whether successful or not.
4) The clipboard is not persistent. It is erased at script exit or computer reboot.
5) Any newly initiated move (:m) or copy(:c) operation overrides the clipboard.
6) Use :dc to display the clipboard content and :ec to erase clipboard.

All relevant clipboard commmands can be found in the clipboard help menu. Type ?clip and hit ENTER to have this menu displayed.

5.8. Recursive move/copy

It is also possible to move or copy files recursively from one/more source folder to a setup destination (target) directory. In order to do this following steps are necessary:
- Go to the destination directory, enter :td and hit ENTER to have it setup as target. Alternatively you can enter the navigation history or favorites menus and set:
  - entry dir as target dir by preceding the entry number with character '+' and hitting ENTER
  - parent dir of entry dir as target by preceding the entry number with character '-' and hitting ENTER
- Go to the directory you need to move/copy files from and hit :M or :C to enter the recursive move/copy mode.
- For each item or group of items you require to transfer enter an appropriate keyword and hit ENTER. After transfer is done a new keyword will be required for the next item or group.
- After entering all keywords and transfering all required items instead of entering a new keyword just hit ENTER to exit the recursive mode.
- If other files from another folder need to be transferred to the target directory go to the next source directory and re-enter the recursive move/copy mode.
- Repeat the above steps until all required files from all source directories are transferred to the destination (target) directory.

Notes:
1) To switch from recursive move mode to recursive copy mode (or vice-versa) you need to exit the current mode (hit ENTER without keyword) and enter the other one by using the appropriate option (:C or :M).
2) The target directory is not persistent. It is reset at script exit or computer reboot.
3) To reset the target directory just enter :etd and hit ENTER. Setting up a new dir will then be required for initiating new recursive operations.
4) To display the target directory (if any) enter :dtd and hit ENTER. If the directory is invalid (e.g. has been erased/moved in the meantime) you will be prompted to set a new one.
5) To set a new target directory just (re-)enter :td and hit ENTER. If a target dir is already in place it will get overridden by the new target folder.
6) If the target directory is setup from the navigation menu the missing directory case is handled as follows:
   - for the missing directory of the entry the same steps are requires as when visiting the directory through the menu. For more details regarding missing directories from menu check section 7.
   - for the missing parent directory of the entry a warning message will be shown, no further actions enforced from menu.

All relevant recursive move/copy commmands can be found in the clipboard help menu. Type ?clip and hit ENTER to have this menu displayed.

5.9. Getting help

The main navigation options can be viewed by entering the ? character and hitting ENTER in navigation mode. The application remains in "default mode" meaning the user can continue to use the navigation and commands functionality without the need to exit the help menu. This is slightly different from the BASH-only version where the user had to quit the help dialog to be able to continue to use the application. The main help menu is complemented by two specialized menus, namely the clipboard/recursive help (type ?clip and hit ENTER) and the batch renaming help menu (?ren + ENTER). For more details about these functionality areas check sections 5.7, 5.8 and 8.

5.10. Settings

For specific functionality domains settings files have been created. These have names ending with _settings.py are directly accessible by the _backend.py functions. The settings files contain specific variables that can be modified by user for doing adjustments in the behavior of the application. Examples of possible changes are:
- changing the minimum number of characters a command should have so it gets memorized in the commands history
- changing the names and location of the history files (currently they are all located in the user home directory)

Currently settings are available for:
- navigation (navigation_settings.py)
- commands (commands_settings.py)
- batch renaming of files contained in the current directory (rename_settings.py)

For more details consult these files and read the comment added to each settings variable.

5.11. Toggling between menus

When the user is in one of the following menus it is possible to toggle to its "counterpart" menu:
- navigation history -> to navigation favorites
- navigation favorites -> to navigation history
- commands history execute mode -> to edit mode
- commands history edit mode -> to execute mode

The user just has to enter option :t while in one of these menus and hit ENTER.

Please note that no toggling occurs if the counterpart menu has no entries available. Instead the same error message is displayed as if the user tried to enter this menu from the start.

To be noted is that the toggle option works in filtered menus as well. The counterpart will have the same filter applied. Same rule applies here: if the counterpart does not have any entries when applying that filter then no toggling will occur and the corresponding error message is displayed.

If the user enters the toggle option without being in either of the above menus, then a distinct error is displayed stating toggling is not possible.

The toggle option is particularly useful in filtered menus by saving the effort of manually re-entering the filter for the menu counterpart (most commonly when the user wants to edit a command instead of directly executing it).

Note: by re-entering option :t the user toggles back to previous menu (and so on...). This back-and-forth toggling is obviously not applicable if the counterpart menu has no available entries.

5.12. Re-entering the last used filter

For more details regarding filtered history please consult section 6.5.

If a filter has been previously input for navigation/commands it can be re-entered by using a (short) specific keyword without the user requiring to re-enter the actual filter keyword. The last entered filter keyword is displayed on the main navigation page, namely:
- last used navigation filter
- last used commands filter

Following keywords can be entered to enter the last used filter:
- :n for applying the last used navigation filter to the navigation history
- :N for applying the last used navigation filter to the favorites
- :f for applying the last used commands filter to commands history in execute mode
- :F for applying the last used commands filter to commands history in edit mode

Notes:
- the filter might yield no results (same as when applying it directly by entering the filter keyword)
- if no filter has been previously entered then an error message is displayed and no filtering is performed
- the filter is displayed on the main page exactly as previously input by user from keyboard. This means it might for example contain preceding and/or trailing whitespaces. This is not the case with the filter displayed in the filtered navigation/command menu (a.k.a. "applied filter". This one is actually the "pre-processed" filter which was used to perform the concrete filtering. The ones displayed on the main navigation page could be called "raw filters" as they represent the user "raw" input.

6. THE HISTORY FUNCTIONALITY

Each time a directory is visited or a command is executed, the event is tracked in a history file. There are three different history sections available:
- recent history
- persistent history
- excluded history (only for navigating to directories)

The command history only tracks the commands initiated in navigation mode, namely the ones preceded by the : character. It is completely separate from standard BASH history, which tracks commands executed when navigation mode is disabled.

6.1. Recent history

Most recently visited directory paths or executed commands are mentioned here. It has a limited number of entries (which is specified by a variable from navigation_settings.py / commands_settings.py) and older content is continually overridden.

The entries are stored "in order" but duplicates are not allowed. If the maximum number of entries has been reached, the least recently visited path/executed command is taken out (circular buffer behavior). Unlike persistent history (see next section), the entries are NOT displayed to the user in a sorted fashion but instead they are shown in reverse order of their access (first entry is the last visited directory or executed command).

A subset of the recent history is the quick history, see section 6.8.

6.2. Persistent history

All paths except the ones from excluded history are mentioned here along with the number of visits. When a new directory is visited the first time on the current day the number of visits is incremented. Further visits on the same day are not taken into account. This prevents unrealistic reporting which might occur if a directory has been entered many times during a day and then remains unvisited for a long time.

Also if the previous directory is the same with the visited directory the persistent history is not updated.

The file is sorted each time it is updated and the most visited paths are added to a consolidated history file.

The same behavior is implemented for executed commands except there is no excluded history to be taken into account.

The persistent history holds an unlimited number of entries. However only a limited number (specified by a variable from navigation_settings.py / commands_settings.py) is displayed in the unified menu (consolidated history), namely the ones that have been visited/executed the highest number of times.

6.3. Consolidated history

This file consolidates the entries contained in the previous 2 files. A unified interface is provided to the user for accessing the history.

6.4. Excluded history

When a directory is added to favorites its entry from the persistent history file is added to this file. This way the number of visits continues to be tracked (same tracking mechanism as for persistent history) and in the same time the path is separated from consolidated history.

When the directory is removed from favorites the entry is moved back to persistent history with the actual number of visits.

If the directory hadn't been visited prior to adding to favorites (e.g. if adding it by calling the addToFavorites function with the directory path as argument when in another directory) an entry with 0 visits is created in the excluded history file. If the directory is removed from favorites before visiting it the entry is removed both from favorites file and excluded history and nothing is added to persistent history.

There is no excluded history for commands. For "favorite commands" using of standard aliases is recommended.

6.5. Filtered history

Both for visited directories and commands there is also the possibility to filter the persistent history (whole file) based on a search keyword. The search will find all matches but only display a limited number of results on screen. This limitation is implemented for efficiency purposes. By modifying a variable in the navigation_backend.py or commands_backend.py it is possible to modify this limit (however I recommend keeping it low).

Once the search results are displayed please select the number of the required entry from the menu so it is executed/visited. The filtered history menus behave the same as the consolidated menus regarding usage.

The same filtering mechanism also applies to favorite directories.

To filter visited paths enter << followed by the search keywoard and hit ENTER in navigation mode. For example enter <<abcd to find the directory /home/user_a/abcdefgh.

To filter favorite paths enter >> followed by the search keyword and hit the ENTER key.

To filter executed commands enter:
- :< followed by keyword to display filtered entries so one is selected for executing (same behavior as when entering :< to display the consolidated command history). Example: type :<abc to search for echo zabcd (exec)
- :: followed by keyword to display filtered entries so one is selected for editing (same behavior as when entering :: to display the consolidated command history). Example: type ::adg to search for echo zadgb (edit and exec)

In the above examples the search keyword contains a single filter. However both for visited paths and executed commands it is possible to use multiple filters. These should be separated by commas, i.e. keyword should have the format: [filter_1],[filter_2],...,[filter_n]. Each keyword filter is being used for conducting a separate search. Search results are AND-ed. For example if the user enters <<abc, def then results matching BOTH 'abc' and 'def' are being displayed. Note that for each filter the preceding and trailing whitespaces are being ignored (for example when entering :<    abc, def the filters are 'abc' and 'def'). Only spaces contained within filter are being taken into consideration, e.g. <<abc, d ef implies using 'abc' and 'd ef' as filters. This is especially useful for finding commands as these might also contain spaces.

Last but not least each individual filter is counted as a regular expression so the specific regex syntax can be used. However this should be valid otherwise no search results will be returned. For example entering ::* will yield no results.

Notes:
- all persistent history file entries (including the ones not displayed in the consolidated menu) are being searched for the given keyword. This gives the user a chance to reuse the less visited/executed paths/commands as well.
- the search is case-insensitive, meaning you can enter <<abcd for /home/aBcd retrieval
- the number of spaces within search keyword filter is relevant and should be the right one for identifying the substring in the command/path. For example you should enter :<cho ab and not :<cho  ab to find the echo abdcgijk command. As already mentioned before, preceding and trailing spaces are ignored for each filter.
- if the number of found entries is higher than the displayed ones try to narrow down the search if the required path/command is not visible. This can be done by modifying the filter(s) within keyword or by adding new filters. Feel free to use regex specific syntax as well if required.
- also if no match was found try to modify the search keyword until getting the desired result. If the result is still not obtained it is likely that the required entry is not in the persistent history file (maybe it had been deleted at the last history reset)
- the excluded history is not contained in the paths used as navigation history filtering base. The search is performed only in the persistent history files. It is possible to filter excluded history separately by using prefix >> (favorite paths filtering)
- empty filters are ignored. For example if the user enters <<,,abc only abc is being used for the search. If no valid (not empty) filters have been entered then no results are being displayed. Please note that filters containing only whitespaces are also considered empty.
- it is also possible to search for entries that don't contain a specific keyword. In order to do this without using specific regular expression, the user could enter the keyword preceded by the '-' character. This is the same (yet much easier) as writing ^((?!keyword).)*$ which would be rather messy. For example by entering dir1, -dir2 (or vice-versa) the entries that contain dir1 but not dir2 are being searched for. Say there are two distinct directories, namely /home/user1/dir1 and /home/user1/dir2/dir1. By using the mentioned filters combination only the first entry will be displayed. This is particularly useful when two similar directory structures with different base directories exist and the user is interested in navigating in only one of them. Same can be used for similar commands, e.g. two shell commands that differ by only one option. Please note that the expanded regex syntax is being displayed as last used navigation/commands filter.
- the keyword search is actually a regex match as each keyword is a regular expression construct

6.6. Adding commands to history based on command string size

It is possible to setup the minimum number of characters a command should contain in order to be stored into the command history file. This is done by setting up the min_command_size variable in commands_settings.py. For example by setting min_command_size=10 each command with less than 10 characters will be prevented from being included into the command history. The characters include the spaces but not the : character used for entering the command in navigation mode. This rule can be bypassed if more spaces are being included in the command (if the command has a single word the spaces should be added before the word). An alternative is to set the minimum number of characters to 0 in the settings file.

For example:
:echo abcd #will not be included in command history (less than 10 characters - a total of 9, including space, excluding : )
:echo  abcd #will be included in command history (2 spaces this time)
:echo #will not be included, no matter how many spaces are entered after echo
:      echo #will be included, there is a total of 10 spaces, 6 spaces before the echo word

Note: this setting does not affect storing the command in the "last executed shell command" buffer which is updated each time a command is executed no matter how many chars the command contains. The content of this buffer is volatile and is erased once exiting the goto_app.py script.

6.7. Sensitive commands

It is possible to mark specific commands as sensitive. This is not done via script execution but by manually modifying the value of the sensitive_commands_keywords variable in commands_settings.py by adding a search keyword to the set. For example if the keyword is 'rm ' every command containing this string will be marked as sensitive (the space is important as you would not like any command containing this substring (like 'echo permanent' to be added to the sensitive area). This functionality is useful for preventing accidental execution of commands that produce irreversible unwanted results. Examples of such commands are: rm, rmdir, mv.

How this actually works:
- if the user chooses a command from the commands history menu (in execute mode) the script will check if the command string contains one of the substrings that had been added to sensitive_commands_keywords
- if the command contains (at least) one of these substrings a prompt will be displayed asking the user to confirm the command execution
- the user should enter y (yes) for confirming and n (no) for declining. The option is case insensitive but should be one of these two.
- if the operation is confirmed the command will get executed, otherwise it will be cancelled

Note:
- the functionality is active only when accesing the command from any commands history (persistent, recent, filtered) only in EXECUTE mode. It does not get applied in EDIT mode or when manually entering a command from navigation mode by preceding it with the : character.
- also the functionality does not get applied when repeating the previously executed shell command by entering the special option :- from navigation menu

I strongly recommend using this option and carefully checking the command string prior to choosing the 'y' option. The principle "better safe than sorry" has a good application in this situation.

6.8. Quick history

The quick history is a subset of the recent history. Currently this is only available for navigation, but it might get implemented for commands as well (in a future changeset).

The quick navigation history is displayed within main navigation and help menus. It contains the last visited directories. The number of displayed entries cannot exceed the size of the recent history (instead it can be smaller resulting in a subset). It is recommended to keep the count as small as possible in order to be able to identify the required entry rapidly (hence quick history) and then navigate to the directory.

The navigation to the chosen entry is performed by entering < followed by entry number. Please note that the number should be valid, i.e. it needs to be a valid integer pointing to one of the listed entries. If the entry number is out-of-range or contains invalid (non-numeric) characters (see below notes too), then an error will be triggered. The user should correct the input and retry.

By default the quick navigation history is disabled, so it doesn't clutter the main menu/help menus unnecessarily. To enable it, enter option :qn from main navigation page or another menu. To disable it, enter the same option again. Please note that the quick history is persistent during the entire session unless disabled. It goes off when exiting the script.

Another caveat is that the quick navigation history can only be used from the places where it is displayed. These are:
- the main navigation page
- the help sub-menus (which are also considered part of the main navigation context)

If the user attempts to access a quick entry from another context (e.g. enters <2 while in the filtered navigation history menu), then an error is triggered mentioning that the context is not appropriate. The context is automatically switched to main navigation page, and the user can re-enter the quick navigation choice. This time the navigation should be successful unless the quick history is disabled or the entry is invalid. The reason for implementing this menu(context)-based restriction is that it needs to be ensured the user is fully aware of the chosen entry before executing it. This would be of utmost importance if a similar quick menu is implemented for commands.

Last but not least, it is also possible to visit the parent directory from the chosen entry. To do this instead of < enter ,, followed by entry number. For example if directory /home/myUserName/Documents is displayed at position 2 in quick history, then simply enter ,,2 in order to visit its parent /home/myUserName. All above mentioned quick history rules apply here.

Notes:
- to modify the number of displayed entries, please change the variable q_hist_max_entries from navigation_settings.py to the desired value (default is 5 and it is recommended to keep it small).
- it is allowed to have one or more spaces between the quick history identifier (< or ,,) and the entry number, as long as the number itself is a contiguous integer pointing to an existing quick history entry (e.g. entering <  2 is as valid as entering <2)
- when accessing the parent directory, an empty entry number (namely entering only ,,) is considered invalid and the same error is triggered as when the other validity criteria (mentioned above) are not fulfilled. The user should retry by entering a valid entry number.

7. HANDLING MISSING DIRECTORIES

It can happen that for an entry chosen from one of the 2 above mentioned menus the path doesn't exist anymore. This can happen for various reasons:
- the directory has been deleted
- the directory has been moved, renamed or a combination of both

In this case the user has two options:
- remove the entry from the menus
- remap the path to an existing one (for example when the directory has been renamed) to preserve the number of visits

Note: this functionality is NOT available when choosing the parent dir from the entry. In this case only a warning message will be displayed that the parent dir path is not valid and that the dir and its children could be removed or mapped. The actual removal/mapping can be done by individually selecting each directory (not parent) from the navigation menu (history/favorites). This might also include the parent directory if it is contained within menu in a separate entry.

7.1. Removing the path

When this option is chosen the path is removed from all menus and files. The number of visits is lost.

7.2. Remapping

The user might opt for replacing an invalid path from the navigation menus (history/favorites) with another path. The replacing path might be one that already exists in the menus, one that is contained in history but doesn't have enough visits (or hasn't been recently visited) to be contained in the consolidated history menu or a path that hasn't been visited since the last history reset.

Depending on the above mentioned conditions following scenarios are available:
- an unvisited path will replace the invalid path in the menu the latter one had been contained in and will take the number of visits of the replaced path
- a path with not enough visits or not visited recently enough will show up in consolidated history with the same number of visits that the invalid path had
- a replacing path that is already contained in one of the menus will keep its menu but the number of visits will be updated if the invalid path had more visits

In either case the invalid path is completely removed from all menus.

It is possible to easily choose the replacing path from history/favorites by entering '<' or '>' and hitting ENTER when the user is prompted to enter a replacing path. The user will be brought to the chosen menu from which he can choose one of the paths by entering its number and hitting ENTER. If no path is suitable then the user still has the possibility to enter another path without exiting the chosen menu.

It is not possible to switch between history and favorites menus when choosing the replacing path. The user must first quit the re-mapping process by hitting '!' + ENTER and then restart re-mapping by choosing the invalid path from menus again.

Also when choosing a valid replacing path the current directory will be switched to this path after remapping.

8. RENAMING A BATCH OF ITEMS

It is possible to rename all items from the current directory by using various schemes. Please note that for safety reasons the items that are hidden are excluded from this functionality.

Batch renaming involves two basic operations: adding substrings and removing substrings to/from each item name. This can be done in more ways which will be presented below.

The adding of the substring can be done:
- either by adding a fixed string (like "Photo_") to each item. For example FileA becomes Photo_FileA, FileB becomse Photo_FileB and so on.
- or by adding a number that is then incremented for each item. For example FileA becomes FileA1, FileB becomes FileB2 and so on.

Following renaming schemes are currently supported:
- appending a fixed string to each item name
- appending a number that is incremented for each item
- prepending a fixed string
- prepending a number
- inserting a string by specifying the index within the item name where the insert should occur. For example if the item is FileA, the index is 1 and the string is "_cc" the resulting name will be: F_cc_ileA
- inserting an incrementable number
- deleting a substring from each file. For example if deleting 2 characters at index 1, FileA becomes FeA and FileB becomes FeB.
- replacing a substring with another substring. In addition to file index the number of removed characters should also be given. For example if the file is FileB, the index is 1, the number of removed characters is 2 and the substring to be added is _dd_ the resulting filename is F_dd_eB
- replacing a substring with an incrementable number

It is possible to combine these operations for more complex renaming. However this has to be done in separate sessions as the functionality does not allow executing them "on the fly". Actually I wouldn't even recommend this. In my opinion it is better to check the intermediary results each time an "atomic" operation is performed.

For details regarding the commands to be used please check the renaming help by typing ?ren in the navigation menu and hitting ENTER. For example the command for appending a fixed substring to each item is :ra.

The steps for performing the renaming are as follows:
- navigate to the directory in which items should be renamed
- execute the command for the chosen renaming scheme
- you will enter an interactive menu where you will be prompted to provide all required data
- after entering this data a simulation of the renaming is performed and some before/after examples are displayed. Hit y (yes) or n (no) and press ENTER to perform the actual operation or abort it.

Notes:
1) In the interactive menu it is anytime possible to abort renaming by just hitting ENTER.
2) For renaming by using an incrementing number it is required to mention the starting value in the interactive menu. For example if the initial value is 3 FileA will be renamed FileA3, FileB - FileB4 and so on when choosing append mode.
3) Only valid input parameters are accepted. For example it is not allowed to enter negative indexes for insertion. You will be required to re-enter the param if it is not valid.
4) The system performs some checks based on the entered parameters. The renaming operation will NOT be allowed if any of following conditions occur:
   - duplicates would result from renaming. If for example you remove one character at index 4 from FileA and FileB the resulting names would be File. This would cause the overriding of the content of one of the files by the other. Such an issue might cause a severe data loss.
   - at least one of the items cannot be renamed due to parameters that are not fit for its original name size. For example if 2 characters were required to be removed at index 5 of FileA this operation would not be valid for the simple reason that there is nothing at this index. Even if the other items are eligible (say FileAbcdefgh) the operation is not allowed because each visible item needs to be renamed.
   - also if no visible items are present in the current directory an error will be triggered prior to entering the interactive menu.

9. FALLBACK FOR CURRENT DIRECTORY

In rare situations the current directory might become unavailable. This might happen for example when it has been deleted externally (e.g. by using a separate terminal) or when the permissions have been altered.

When this is the case the application uses a fallback mechanism that replaces the current dir with a preset fallback directory. It is highly recommended to use the home dir as fallback, yet if you would like to use another folder this can be setup in system_settings.py. However you should make sure the fallback dir is valid and accessible at any time.

The fallback mechanism works as follows: when the user tries to execute an operation (e.g. go to another folder) the application performs a sync process. First it is being checked that the current directory is reachable. Then if the current dir is available it continues the operation as per normal process. However if the current dir is not reachable it changes it to the fallback directory and warns the user that the requested operation could not be performed. The user can try again afterwards or choose to execute another operation by taking the current directory change into account.

To be noted:
- the clipboard and recursive transfer are reset at fallback meaning the user will need to re-initiate these processes (with new parameters if required)
- entering the help menus and exiting the application is still possible at any time. In these situations a "silent fallback" is performed. This process is made known to the user by displaying the "(fallback)" keyword along with the path of the current directory.
- on MacOS if Finder synchronization is enabled, when a fallback is performed the sync is preserved and the Finder opens in the fallback directory

The fallback mechanism has been designed for increasing the resiliency of the application by aiding in preventing unwanted crashes. Due to the complexity of the application there might be some places (sub-menus) where it hasn't been implemented (in this case the app might crash), yet in practice it should be seldom required as in most of the situations the current directory should be fully available.

10. MISCELLANEOUS

1) It is possible to erase all entries from history, which means all history files are cleared. When this happens there are no more entries in the consolidated history menu and viewing that menu is disabled (a warning will be issued by script). However the navigation favorites menu retains its entries, yet the number of visits mentioned in excluded history is 0. Type :clearnavigation and hit ENTER in order to clear the navigation history. For command history type :clearcommands and hit ENTER.

2) Unlike the equivalent BASH-only scripts (that can be downloaded from the goToScripts repo: https://github.com/LiviuCP/gotoScripts.git), when exiting the Python script (either by entering ! or CTRL+C / CTRL+D) the current directory is not retained but the terminal will revert to the original directory that was current when launching the goto_app.py.

3) When using CTRL+C or CTRL+D from the clipboard, recursive transfer or rename menus the user returns to the main navigation page and any operation related to these menus is aborted. When hitting these key combinations in any other menu or dialog the application is exited. Please note that CTRL + D might not always work (in some situations it might not have any effect).
