
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

from informationnode.client.api.nodeaction import NodeAction

class NodeActions(object):
    def __init__(self, app, keep_history=False):
        self.app = app
        self.history = dict()

    def do(self, node_url, json, tool="inode-viewer-cli",
            cmd=["raw-cmd"],
            reason="unspecified"):
        action = NodeAction(node_url, json, tool=tool, cmd=cmd)
        if self.keep_history:
            if not node_url in self.history:
                self.history[node_url] = []
            self.history[node_url].append(action)
        return action


