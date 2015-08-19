
'''
information-node - an advanced tool for data synchronization
Copyright (C) 2015  information-node Development Team (see AUTHORS.md)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import argparse
import os
import platform
import re
import socket
import sys
import textwrap

class DoubleLineBreakFormatter(argparse.HelpFormatter):
    """ Retains double line breaks/paragraphs """
    def _split_lines(self, text, width):
        return self._fill_text(text, width, "").splitlines(False)

    @staticmethod
    def _static_fill_text(t, width, indent):
        t = " ".join([s for s in t.replace("\t", " ").strip("\t ").split(" ")\
            if len(s) > 0]).replace("\n ", "\n").replace(" \n", " ")
        ts = re.sub("([^\n])\n([^\n])", "\\1 \\2", t).split("\n\n")
        result = [textwrap.fill(paragraph, width,
            initial_indent=indent, subsequent_indent=indent)\
            for paragraph in ts]
        return "\n\n".join(result).replace("[b]",
        "\033[1m").replace("[/b]", "\033[21m")

    def _fill_text(self, t, width, indent):
        return self._static_fill_text(t, width, indent)

def check_if_node_dir(path, allow_new=False):
    """ Check if the given directory is a valid node path.
        If allow_new is True, an empty directory will also result in a
        positive check.

        Returns (result, msg)

        result: True if check succeeded, otherwise False
        msg: string with an error message in case result was False
    """
    if os.path.exists(path):
        if not os.path.isdir(path):
            return (False, "specified node folder is " +\
                "not a directory")
        contents = os.listdir(path)
        if len(contents) == 0:
            # empty directory.
            if allow_new:
                return True
            else:
                return (False, "specified node folder is " +\
                    "not a valid information node")
        else:
            # check if a valid information node:
            if not os.path.exists(os.path.join(path, "storage")) or \
                    not os.path.exists(os.path.join(path, "identity.secret")):
                return (False, "specified node folder is " +\
                    "not a valid information node")
            return (True, None)
    else:
        if not allow_new:
            return (False, "specified node folder " +\
                "doesn't exist")

        # clean up path a bit:
        path = os.path.normpath(os.path.abspath(path))
        if path.startswith("//"):
            path = path[1:]
        while path.endswith("/"):
            path = path[:-1]
        while (platform.system().lower() == "windows" and\
                path.endswith("\\")):
            path = path[:-1]

        # find out whether the parent dir exists:
        base_dir = os.path.dirname(path)
        if not os.path.exists(base_dir) or not os.path.isdir(base_dir):
            return (False, "cannot create node at " +\
                "specified location because parent directory doesn't" +\
                " exist: " + str(base_dir))

        # create directory as new empty dir:
        try:
            os.mkdir(path)
        except OSError as e:
            return (False, "cannot create node at " +\
                "specified location: " + str(e))
        return (True, None)

def check_if_node_runs(node_folder):
    """ Check if the given node runs. Returns a tuple with
        (result, msg)

        result is: True (node runs), False (node doesn't run), None (error)
        msg: in case of an error, contains a string with the error details.
             If the node is running, this contains the process id.
    """
    # check if pid file exists:
    if not os.path.exists(os.path.join(node_folder, "pidfile")):
        return (False, None)

    # open it up to check for the running process:
    try:
        f = open(os.path.join(node_folder, "pidfile"), "rb")
    except OSError:
        return (None, "failed to read pidfile")
    contents = f.read()
    f.close()

    # check if valid pid:
    try:
        pidnumber = int(contents)
    except ValueError:
        pidnumber = None
    if pidnumber == None or pidnumber < 1:
        return (None, "pidfile has invalid contents. "+\
            "Check if this node has already a process running, and if "+\
            "you are sure this is not the case, remove the pidfile.")

    # check if a process with this pid is running:
    def check_process_running(pid):
        if platform.system() == "windows":
            PROCESS_QUERY_INFROMATION = 0x1000
            processHandle = ctypes.windll.kernel32.OpenProcess(
                PROCESS_QUERY_INFROMATION, 0, pid)
            if processHandle == 0:
                return False
            else:
                ctypes.windll.kernel32.CloseHandle(processHandle)
            return True 
        else:
            try:
                os.kill(pid, 0)
            except OSError:
                return False
            else:
                return True

    if check_process_running(pidnumber):
        return (True, pidnumber)
    
    print("warning: removing stale information node " +\
        "pidfile with pid: " + str(pidnumber), file=sys.stderr)
    os.remove(os.path.join(node_folder, "pidfile"))
    return (False, None)

def get_api_socket_for_node(node_folder):
    """ Tries to open up the node and get an api socket to the data daemon.
        This will fail if the target is not a valid node, or the data daemon
        of it isn't running.
        
        In case of success, this function returns (True, socket).
        Otherwise, (False, error_msg) with error_msg being a string.
    """
    # check if this is a valid node:
    (result, msg) = check_if_node_dir(node_folder)
    if result != True:
        return (False, msg)

    # check if node runs:
    (result, msg) = check_if_node_runs(node_folder)
    if result == None:  # ambiguous breakage (node in invalid state/..)
        return (False, msg)
    if not result:  # node not running
        return (False, "data server of specified node isn't running")

    # open up the unix file socket (linux) or the according port (windows):
    if platform.system().lower() == "windows":
        f = open(os.path.join(node_folder, "api_access.port"), "rb")
        
    else: 
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect(os.path.join(node_folder, "api_access.sock"))

    s.settimeout(5.0)
    return (True, s) 
