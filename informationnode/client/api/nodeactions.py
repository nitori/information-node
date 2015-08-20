
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
import os
import subprocess

class NodeActions(object):
    def __init__(self, app, keep_history=False):
        self.app = app
        self.history = dict()
        self.keep_history = keep_history

    def are_tools_installed(self):
        try:
            with open(os.devnull, 'w') as nullfile:
                subprocess.check_output(["information-node", "--help"],
                    stderr=nullfile)
            return True
        except subprocess.CalledProcessError:
            return False

    def do(self, node_url, json, tool="inode-viewer-cli",
            cmd="raw-cmd", cmd_args=[], answer_is_json=False,
            reason="unspecified"):
        if not self.are_tools_installed():
            # travel up from informationnode.client.api
            tool = os.path.join(os.path.dirname(__file__),
                "..", "..", "..", tool)
        action = NodeAction(node_url, json, tool=tool, cmd=cmd,
            cmd_args=cmd_args, answer_is_json=answer_is_json,
            reason=reason)
        if self.keep_history:
            if not node_url in self.history:
                self.history[node_url] = []
            self.history[node_url].append(action)
        return action


