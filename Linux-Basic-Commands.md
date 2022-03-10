# Linux-Basic-Commands
<p align="center">
<img src="linux.png" height="151">
</p>


 ### Basic List of commands Along with their useful flags

| Commands | Use | Useful flags  | Use
| :------------------ | :------------------ | :------------------ | :------------------ |
| `clear` | Clears the screen of all previous content |
| `pwd` | prints the working directory|
| `ls` | list of all files/folders present in that directory |
| | |  `ls ~` | Contents of The home directory |
| | | `ls ../ `| Gives contents of the parent directory |
| | | `ls > file.txt` | Copies the contents of the ls command into a text file |
| | | `ls -L` | show  information for the file the link references rather than for the link itself |
| `cd` | change directory |
| | |`cd ~` | Changes back to the root folder |
| | | `cd ..` | Navigates back to the previous folder in the heirarchy |
| | | `cd 'directory name'`| This command is used to navigate to a directory with white spaces |
| | | `cd dir_1/dir_2/dir_3` | Navigate between nested folders |
| `echo` | echo is a command that outputs the strings and variables that are passed to it as arguments |
| | | `echo \*.txt`| Displays all the files in the folder with .txt extension |
| | |`echo -n` |Do not output the trailing lines |
| `su` | change user ID or become superuser/ root user |
| `mkdir` | Create the DIRECTORY(ies), if they do not already exist |
| | | `mkdir -p` | Allows to create multiple folders instantly eg/ mkdir -p temp1/temp2
| `mv` | rename or move SOURCE(s) to DIRECTORY |
| | | `mv -i` | Enter interactive mode and asks before overwriting (y/n)
| `cat` |  Concatenate files and print on the standard output. We can see the contents of files using this |
| | | `cat -n` | Gives a number to all the lines
| | | `cat -s` | suppress repeated empty output lines
| `rm` | Removes only files present inside a folder |
| `rmdir` | Removes empty folders entirely |
| | | `rmdir -p folder2/folder 3` | removes the folders recursively (first folder 3 then folder 2)
| `grep` | Works similar to Ctrl+F in windows, used to search for items in a folder  *Note: grep is case sensitive* |
| | | `grep -i` | This flag makes it case **insenstive** |
| | | `grep -n` | Returns the searched string along with its Line number |
| | | `grep -v` | Returns the result of lines **not** matching the search string |
| | | `grep -c` | Returns the result of lines  matching the search string |
| `sort` | sort lines of text files either alphabetically or numerically |
| | | `sort -r` | Sorts the contents in the reverse order **case sensitive** |
| | | `sort -f` | Sorts the contents in the reverse  order **case insensitive** |
| `cp [source] [destination]` | Used to copy files and dirextories (by defautlt it copies only files) |
| | | `cp -R` | Allows us to copy directories **case insensitive**
| | | `cp -v` | Verbose can be used with many commands and it just prints informative messages (shows the status)
|`exiftool`| Allows us to view all the details of an image in any format


**Note: We can use the '|' (pipe) to do multiple operations at once **
**eg. search and sort - `grep aa file1.txt | sort`**
