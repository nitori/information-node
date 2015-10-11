
# information-node

This project offers a new concept of **information nodes** for keeping your
data synchronized between various locations (cloud storage if you will) and
keeping data safe with the help of encryption.

An information node is a directory with data as a database in optimal
storage form along with a process which serves the data or synchronizes it
with other nodes. The contents can be mapped to a regular folder as
editable files like Dropbox, or synced with e-mail/IMAP services, and
more.

The project supports POSIX-systems (Linux, BSD, Mac OS X, ..) and Microsoft
Windows.


# Features

- synchronizes files and e-mails, instant messages, .. for supported services
  between any number of secure locations

- full data encryption for remote backup locations supported

- graphical viewer for browsing a node's contents and working with it

Please note due to the advanced featureset (non-file support for e-mails, ..
and encryption), this tool is slightly more work to learn and use than
the "easy" choices like Dropbox or syncthing.

However, all command line tools have extensive documentation and detailed
commands allowing a very hands on approach in managing your nodes and making
sure everything is synchronized the way you want. You can also use the
graphical viewer to assist you with managing your nodes.


# How to get started / Installation

**WARNING THIS PROJECT IS HIGHLY UNFINISHED. DONT USE**

## Windows

Run viewer.bat

## Linux / BSD / Mac OS X ...

Download this project with git or as .zip and extract it in some folder.
Then, the easiest way of install is:

```bash
sudo python3 setup.py install
```
(inside the information-node project folder)

Afterwards, you can use the included tools directly from the command line.
Enter the following to open up the graphical viewer:

```bash
inode-viewer
```


## Why?

The main idea of information nodes is to allow you to move *all* your data,
not just your files, including all your communication activity, into
possibly encrypted nodes, so as few data as possible is unencrypted and
exposed.

In days where all sorts of attackers and agencies want to spy onto your
data, this should help you set up a trusted storage network with decryption
only possible from your local trusted laptop or with a secured key file you
have on your local usb stick and not in the cloud.


# What data types/protocols are supported?

At this moment, the following data types and protocols can be handled by
an information node network:

* regular files (similar to Dropbox/syncthing)

Please help us expand this list! Volunteer work wanted!


# License

This software is available under the terms of GPLv2 or later.
See LICENSE.txt for details.


# How does this all work?

The technology behind the project is the following:

* Python 3 - https://www.python3.org

* PyCrypto - https://www.dlitz.net/software/pycrypto/
  (the files are encrypted with an AES key which itself is encrypted using
  RSA)

* python-gnutls / GnuTLS - http://www.gnutls.org/
  (TLS encryption for node-to-node communication)

* PyGObject/GTK3 - https://wiki.gnome.org/PyGObject
  (for the inode-viewer)


