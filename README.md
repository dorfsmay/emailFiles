# emailFiles
python script to send files via email to multiple recipients.

It assumes that the files are images and in a format supported by python pillow,
and reduce their size to a 1080x1080 if they are larger.

Initial version from 2010.

## Usage
This script uses a slightly modified version of ini files. The files need to
be in the directory where the script is run from. The data can be split in
several files, all ini files are read and their content is consolidated.

### Required sections
Three sections are required:
* `[main]` which can contain
    * `from`: email address to be set in the FROM field
    * `maximum`: maximum number of files to be sent during each run
* `[bcc]`: a list of email addresses to be use in the BCC field. One address per line
* `[files]`: a list of files to be sent

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

