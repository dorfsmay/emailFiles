# emailFiles
python script to send files via email to multiple recipients.

It assumes that the files are images and in a format supported by python pillow,
and reduce their size to a 1080x1080 if they are larger.

Initial version from 2010.

## Usage
This script uses a slightly modified version of ini files:
  * a line with a key but no value (no equal sign) will defaults to a value of True

The scripts takes files and directory as arguments. Files are assumed to be (modified) ini files, all ini files will be read from arguments that are directories. All ini files content will be merged. If a key is repeated, the value read last will be used, but there is no guarantee on the order the files are read.

### Required keys
* in `[main]` at least one of `to`, `cc` or `bcc`
* the section `[files]`, however it can be empty

### Other keys
Three sections are required:
* `[main]`
    * `from`: email address to be set in the FROM field
    * `maximum`: maximum number of files to be sent during each run

Once a file is sent it will removed from the list of files.

## To Do
- only try to reduce  size for images (so script could be used to send pdf, txt files etc...)
- pick a license or pub domain + add to repo/script
- look at sending a single message to multiple recipient within a domain
- Remove work-around for an old python3 bug.
- test/fix unicode in title 
- review / modernise code for current versions of python3

## Dependencies
- python3
- python3 pillow

