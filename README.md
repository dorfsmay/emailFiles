# emailFiles
python script to send files via email to multiple recipients.

It assumes that the files are images and in a format supported by python pillow,
and reduce their size to a 1080x1080 if they are larger.

Initial version from 2010 (explains some of the oddness)


## Usage
This script uses a non-standard ini files:
  * a line with a key but no value (no equal sign) will defaults to a value of True

The scripts takes files and directory as arguments. Files are assumed to be (non-standard) ini files, all ini files will be read from arguments that are directories. All ini files content will be merged. Duplicated key should result in a failure.

Once a emails have been sent for a file, that file name is removed from the ini files. For this reason it is recommended to keep the list of files to be sent (the `[files]` section) in a separate files.

### Required keys
This is just documentation and inaccurate by definition. Check the `verify_required_config_parameters()` function.
* in `[main]` at least one of `to`, `cc` or `bcc`
* `maxfiles`: maximum number of files to be sent during each run
* the section `[files]`, however it can be empty

### Other keys
* `[main]`
    * `from`: email address to be set in the FROM field
    * `smtp_server`: server through which mail is sent. Default: `localhost`
    * `smtp_port`: port number to connect to the smtp server. Default: 587
    * `tls`: true/false. Use `smtplib.SMTP_SSL` instead of `smtplib.SMTP`. Default: `false`
    * `user_id`: user id to authenticate the smtp connection. If not present no authentication will be attempted. If present, the script will prompt for a password.

Once a file is sent it is removed from the list of files.

### Example ini file
```
[main]
from:  Bob and Linda <belchers@example.com>
maxfiles: 5
smtp_server: mta.example.com

[cc]
gene@example.com
louise@example.com

[bcc]
tina@example.com

[files]
/home/bob/photos/sexy_dance_fighting.jpeg
/home/bob/photos/Weekend_at_Morts.jpeg
/home/bob/photos/bob_selfie.jpeg
```

## To Do
- only try to reduce  size for images (so script could be used to send pdf, txt files etc...)
- make file size a parameter with a sane default
- test/fix unicode in title
- pick a license or pub domain + add to repo/script
- do something with emails that cannot be delivered!
- look into sending a single message to multiple recipient within a domain
- setup 'subjectpattern' in main to allow a custom transformation from filename to subject line
- allow to setup a domain rather than an smtp server, and make an mx lookup to find the server
- Remove work-around for an old python3 bug ("issue # 11156").

- review / modernise code for current versions of python3

## Dependencies
- python3
- python3 pillow


