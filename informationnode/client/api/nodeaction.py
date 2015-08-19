
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
        self._done = False

    def run(self):
        self._done = True

    @property
    def done(self):
        return self._done 


