# emailFiles
python script to send files via email to multiple recipients.

It assumes that the files are images and in a format supported by python pillow,
and reduce their size to a 1080x1080 if they are larger.

Initial version from 2010.

# To Do
- only try to reduce  size for images (so script could be used to send pdf, txt files etc...)
- pick a license or pub domain + add to repo/script
- look at sending a single message to multiple recipient within a domain
- Remove work-around for an old python3 bug.
- test/fix unicode in title 
- review / modernise code for current versions of python3

# Dependencies
- python3
- python3 pillow

