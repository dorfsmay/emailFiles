#!/usr/bin/env python3

#
# Copyright, Yves Dorfsman, Calgary 2010
#
#
import tempfile
import PIL.Image
import os.path
import collections
import copy


def myencoder(msg):
    """
    See python issue # 11156.
    """
    from base64 import encodebytes as _bencode

    orig = msg.get_payload()
    encdata = str(_bencode(orig), "ascii")
    msg.set_payload(encdata)
    msg["Content-Transfer-Encoding"] = "base64"


def email_file(meta_data, msg, file):
    import smtplib
    import mimetypes
    import email.message
    import email.encoders
    import email.mime.base
    import email.mime.text
    import email.mime.image
    import email.mime.audio

    fn = os.path.basename(file)

    # 'blabla_etc.jpeg' --> 'blabla etc'
    dot = fn.rfind(".")
    msg["Subject"] = fn.replace("_", " ")[:dot]

    ctype, encoding = mimetypes.guess_type(file)
    if ctype is None or encoding is not None:
        ctype = "application/octet-stream"

    maintype, subtype = ctype.split("/", 1)
    if maintype == "text":
        with open(file) as fp:
            # Note: we should handle calculating the charset
            att = email.mime.text.MIMEText(fp.read(), _subtype=subtype)
    elif maintype == "image":
        with open(file, "rb") as fp:
            att = email.mime.image.MIMEImage(fp.read(), _subtype=subtype)
    elif maintype == "audio":
        with open(file, "rb") as fp:
            att = email.mime.audio.MIMEAudio(fp.read(), _subtype=subtype)
    else:
        with open(file, "rb") as fp:
            att = email.mime.base.MIMEBase(maintype, subtype)
            att.set_payload(fp.read())
        # Encode the payload using Base64
        email.encoders.encode_base64(att)

    att.add_header("Content-Disposition", "attachment", filename=fn)
    msg.attach(att)

    composed = msg.as_string()

    smtp_sender = smtplib.SMTP
    if meta_data["tls"]:
        smtp_sender = smtplib.SMTP_SSL

    s = smtp_sender(meta_data["smtp_server"], meta_data["smtp_port"])
    if "user_id" in meta_data:
        s.login(meta_data["user_id"], meta_data["password"])
    s.sendmail(meta_data["from"], meta_data["send_to_list"], composed)
    s.quit()


def prepare_generic_message(ini_dict):
    import email.mime.multipart

    msg = email.mime.multipart.MIMEMultipart()

    if "from" in ini_dict["main"]:
        msg["From"] = ini_dict["main"]["from"]["data"]
    send_to_list = []
    if "to" in ini_dict:
        send_to_list.extend(ini_dict["to"].keys())
        msg["To"] = ", ".join(ini_dict["to"].keys())
    if "cc" in ini_dict:
        send_to_list.extend(ini_dict["cc"].keys())
        msg["Cc"] = ", ".join(ini_dict["cc"].keys())
    if "bcc" in ini_dict:
        send_to_list.extend(ini_dict["bcc"].keys())
    return msg, send_to_list


class iniFileFormat(dict):
    """
    We don't use configparser because secionts need to be odered dictionary
    it does not accept parameters without right-hand-side values. We want
    to be able to add parameters such as:

    [cc]
    joe@example.com
    jane@example.com

    Also, we need to keep track of file names and line numbers.

    This parser does not implement line continuation.

    It returns a dictionary such as:
    { 'cc':
             { 'joe@example.com':
                                  {
                                  'data': True,
                                  'filename': '/path/to/file'
                                  'linenumber': 7
                                  }
             }
             { 'jane@example.com':
                                  {
                                  'data': True,
                                  'filename': '/path/to/file'
                                  'linenumber': 12
                                  }
             }
    }
    """

    def __init__(self, slurped_list=None, filename=None):
        dict.__init__(self)
        if slurped_list is not None:
            if filename is None:
                raise ValueError("filename cannot be empty.")
            self.parse(slurped_list, filename)

    def __add__(self, other):
        """
        Allows to read configuration from different files and merge them together.
        You can repeat a section in a different file, but parameter within
        a section cannot be repeated.
        """

        allsections = list(self.keys()) + list(other.keys())
        # make a set of unique sections accross both objects.
        allsections = set(allsections)

        sum = iniFileFormat()

        for section in allsections:
            if section not in self:
                sum[section] = copy.deepcopy(other[section])
            elif section not in other:
                sum[section] = copy.deepcopy(self[section])
            else:
                # Check for duplicates accross files
                k = other[section].keys()
                for x in k:
                    if x in self[section].keys():
                        t = (
                            'Duplicate value "'
                            + x
                            + '" in section "'
                            + section
                            + '" in files:\n'
                            + self[section][x]["filename"]
                            + "\nand\n"
                            + other[section][x]["filename"]
                        )
                        raise ValueError(t)
                sum[section] = copy.deepcopy(self[section])
                sum[section].update(other[section])
        return sum

    def parse(self, slurped_list, filename):
        import re

        section = None

        if slurped_list is None or type(filename) is not str:
            raise ValueError
        section_pattern = re.compile(r"^\[(.*)\]$")

        for ln, line in slurped_list.items():
            line = line.strip()
            if line.find("#") == 0:
                continue
            if line.find(";") == 0:
                continue
            if line == "":
                continue

            found = section_pattern.match(line)
            if found:
                section = found.group(1).lower()
                if section not in self:
                    self[section] = collections.OrderedDict()
                continue

            if section is None:
                t = "Parameters stated before a section was defined in file " + filename
                raise ValueError(t)

            idx = line.find(":")
            if idx < 0:
                idx = line.find("=")

                if idx < 0:
                    k = line
                    v = True
                else:
                    k = line[:idx]
                    v = line[idx + 1 :]
            else:
                k = line[:idx]
                v = line[idx + 1 :]

            # stop if duplicate in the same file
            if k in self[section]:
                t = (
                    'Duplicate value "'
                    + k
                    + '" in section "'
                    + section
                    + '" in file:\n'
                    + filename
                )
                raise ValueError(t)

            # do the work
            self[section][k] = {}
            self[section][k]["linenumber"] = ln
            self[section][k]["data"] = v
            self[section][k]["filename"] = filename


def slurp_files(files, slurped_dict, lock_files):
    """
    Slurp files from argument, or all .ini files from directories in
    argument and returns a consolidated iniFileFormat dictionary.

    "files" needs to be a python list, listing the files.

    slurped_dict is a regular dictionary, but, it is populated with
    ordered dictionaries from collections. Each ordered dictionary
    is the content of a file, indexed by line number at the time of
    reading. We need to line numbers to be able to delete lines. It
    has to be ordered as we use the values to re-write the file.

    If a name is a directory, it will parse all .ini files in that directory.
    """

    import os

    ini = iniFileFormat()

    for f in files:
        if not os.path.exists(f):
            raise ValueError("Name " + f + " is not a file nor a directory.")
        if os.path.isdir(f):
            import glob

            f = os.path.join(f, "*.ini")
            f = glob.glob(f)
            ini += slurp_files(f, slurped_dict, lock_files)
        else:
            # Try to create a unique copy, let the error rise if a the file exists
            lhs = os.path.dirname(f)
            rhs = os.path.basename(f)
            lock_file_name = lhs + os.path.sep + "." + rhs + ".swp"
            try:
                fd = os.open(
                    lock_file_name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600
                )
                lock_files.append(lock_file_name)
            except OSError:
                t = "File " + f + " seems busy. Check why the lock file "
                t += lock_file_name + " is present. Aborting."
                raise OSError(t)

            slurped_dict[f] = collections.OrderedDict()
            with open(f, "rt") as openedf:
                for k, v in enumerate(openedf):
                    slurped_dict[f][k] = v

            ini += iniFileFormat(slurped_dict[f], f)

    return ini


def delete_lock_files(file_list):
    import os

    for f in file_list:
        # print('deleteing ', f)
        os.unlink(f)


def fix_size_of_file(dir, img_name):
    """Return image with a maximum side of maxside"""
    maxside = 1080
    new_name = os.path.split(img_name)[-1]
    new_name = os.path.join(dir, new_name)
    img = PIL.Image.open(img_name)
    if 1080 < max(img.size):
        img.thumbnail(
            (
                maxside,
                maxside,
            )
        )
    img.save(new_name)
    return new_name


def verify_required_config_parameters(ini_dict):
    # Throw an exception if missing a required config
    if "main" not in ini_dict or "from" not in ini_dict["main"]:
        raise ValueError('Missing "From" in seciton main')

    if "maxfiles" not in ini_dict["main"]:
        raise ValueError(
            'Missing "maxfiles" (maxium number of files to send) in seciton main'
        )
    recipient = 0
    if "to" in ini_dict:
        recipient += len(ini_dict["to"])
    if "cc" in ini_dict:
        recipient += len(ini_dict["cc"])
    if "bcc" in ini_dict:
        recipient += len(ini_dict["bcc"])
    if recipient < 1:
        raise ValueError("No recipient specified.")

    if "files" not in ini_dict:
        raise ValueError("No files section.")


def extract_meta_data(ini_dict):
    from getpass import getpass

    meta_data = dict()
    # setup defaults
    meta_data["smtp_server"] = "localhost"
    meta_data["smtp_port"] = 587
    meta_data["tls"] = False

    meta_data["from"] = ini_dict["main"]["from"]["data"]
    if "smtp_server" in ini_dict["main"]:
        meta_data["smtp_server"] = ini_dict["main"]["smtp_server"]["data"].strip()
    if "smtp_port" in ini_dict["main"]:
        meta_data["smtp_port"] = int(ini_dict["main"]["smtp_port"]["data"].strip())
    if "tls" in ini_dict["main"]:
        if init_dict["main"]["tls"]["data"].strip().lower() not in ("0", "false"):
            meta_data["tls"] = True
    if "user_id" in ini_dict["main"]:
        meta_data["user_id"] = ini_dict["main"]["user_id"]["data"].strip()
        meta_data["password"] = getpass()
    return meta_data


def main(args):
    # args:  python list, containing files, or directories

    import atexit

    slurped = dict()
    lock_files = []

    atexit.register(delete_lock_files, lock_files)

    # read the files
    ini_dict = slurp_files(args, slurped, lock_files)

    # Will throw an exception if missing a required config
    # We let it bubble up and die (early termination)
    verify_required_config_parameters(ini_dict)
    meta_data = extract_meta_data(ini_dict)
    maxfiles = int(ini_dict["main"]["maxfiles"]["data"])

    list_of_files = list(ini_dict["files"].keys())
    list_of_files = list_of_files[:maxfiles]
    tempdir = tempfile.TemporaryDirectory()
    generic_msg, send_to_list = prepare_generic_message(ini_dict)
    meta_data["send_to_list"] = send_to_list

    for attchm in list_of_files:
        fixed_size_file = fix_size_of_file(tempdir.name, attchm)
        msg = copy.deepcopy(generic_msg)
        email_file(meta_data, msg, fixed_size_file)
        fn = ini_dict["files"][attchm]["filename"]
        ln = ini_dict["files"][attchm]["linenumber"]
        del slurped[fn][ln]
        open(fn, "wt").writelines(slurped[fn].values())


import sys

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        main(sys.argv[1:])
    else:
        raise ValueError("Needs at least one directory or file name.")
