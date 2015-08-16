
# Information node

This project offers a new concept of **information nodes** for keeping your
data synchronized between various locations (cloud storage if you will) and
keeping data safe with the help of encryption.

It supports POSIX-systems (Linux, BSD, Mac OS X, ..) and Microsoft Windows.

The main differences to Dropbox or syncthing are:

* no central server, instead peer-to-peer (similar to syncthing)

* support for non-file data like e-mails, IM, ... including gateways that
  automatically fetch your e-mails, messages, etc into a node and sync it into
  your network.

* graphical viewer that browses and searches all the data easily

* built-in support for encryption, including storing data on a remote location
  just as fully asynchronously encrypted blob that can only be decrypted at
  your main site

Please note due to the advanced featureset (non-file support for e-mails, ..
and encryption), this tool is slightly more work to learn and use than
the "easy" choices like Dropbox or syncthing.

However, all command line tools have extensive documentation and detailed
commands allowing a very hands on approach in managing your nodes and making
sure everything is synchronized the way you want. You can also use the
graphical viewer to assist you with managing your nodes.

## Why?

The main idea of information nodes is to allow you to move ALL your data,
not just your files, including all your communication activity, into
possibly encrypted nodes.

In days where all sorts of attackers and agencies want to spy onto your
data, this should help you set up a trusted storage network with decryption
only possible from your local trusted laptop or with a secured key file you
have on your local usb stick and not in the cloud.

# How to get started / INSTALL

** WARNING THIS PROJECT IS HIGHLY UNFINISHED. DONT USE **

## Windows

1. Install latest Python 3 release for windows: https://www.python.org/downloads/windows/

2. Download this project as .zip if you haven't already: https://github.com/information-node/information-node/archive/master.zip

3. Run viewer.bat and enter the python installation path when it asks you

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

# What exact data types and protocols are supported?

At this moment, the following data types and protocols can be handled by
an information node network:

* regular files (similar to Dropbox/syncthing)


