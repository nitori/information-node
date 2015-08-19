
'''
information-node - an advanced tool for data synchronization
Copyright (C) 2015  Information Node Development Team (see AUTHORS.md)

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

import subprocess

class NodeAction(object):
    def __init__(self, node_path, json_request,
            tool="inode-viewer-cli", cmd="raw-cmd"):
        self.node_path = node_socket
        self.tool = tool
        self.cmd = cmd
        self.json_request = json_request
        self._done = False

    def run(self):
        """ Returns (True, json_obj) on success, and
            (False, error_msg) on failure.
        """
        program = subprocess.Popen([self.tool] + self.cmd,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout_data, stderr_data) = program.communicate(
            input=self.json_request)
        self._done = True
        try:
            json_obj = json.loads(stdout_data)
        except ValueError:
            return (False, stdout_data)
        return (True, json_obj)

    @property
    def done(self):
        return self._done 


