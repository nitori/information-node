
'''
information-node - an advanced tool for data synchronization
Copyright (C) 2015  Information Node Development Team (see AUTHORS.md)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.


In addition, as a special exception, the copyright holders give
  permission to link the code of portions of this program with the
  OpenSSL library under certain conditions as described in each
  individual source file, and distribute linked combinations
  including the two.
You must obey the GNU General Public License in all respects
  for all of the code used other than OpenSSL.  If you modify
  file(s) with this exception, you may extend this exception to your
  version of the file(s), but you are not obligated to do so.  If you
  do not wish to do so, delete this exception statement from your
  version.  If you delete this exception statement from all source
  files in the program, then also delete it here.

'''

from informationnode.client.api.nodeaction import NodeAction
import logging
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
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def do(self, node_url, json, tool="information-node",
            cmd="raw-cmd", cmd_args=[], answer_is_json=False,
            reason="unspecified"):
        if not self.are_tools_installed():
            # travel up from informationnode.client.api
            tool = os.path.join(os.path.dirname(__file__),
                "..", "..", "..", tool)
        action = NodeAction(node_url, json, tool=tool, cmd=cmd,
            cmd_args=cmd_args, answer_is_json=answer_is_json,
            reason=reason)
        print("keep history: " + str(self.keep_history))
        if self.keep_history:
            print("putting into history: " + str(action))
            if not node_url in self.history:
                self.history[node_url] = []
            self.history[node_url].append(action)
        return action


