
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

import json
import logging
import subprocess

class NodeAction(object):
    def __init__(self, node_path, json_request,
            tool="information-node", cmd="raw-cmd",
            cmd_args=[], answer_is_json=True, reason=None):
        self.answer_is_json = answer_is_json
        self.node_path = node_path
        self.tool = tool
        self.reason = reason
        self.cmd = cmd
        self.cmd_args = cmd_args
        self.json_request = json_request
        self._done = False

    def __repr__(self, redact_details=False):
        return "NodeAction(\"" + str(self.node_path) + "\", " +\
            "\"" + (self.json_request if not redact_details else "REDACTED")\
            + "\", tool=\"" + self.tool + \
            "\", cmd=\"" + self.cmd + "\")"

    def run(self):
        """ Returns (True, json_obj) on success, and
            (False, error_msg) on failure.
        """
        logging.debug("[client.api.NodeAction] Running action " +\
            self.__repr__(redact_details=True))
        program = subprocess.Popen([self.tool] + \
            [self.cmd] + [self.node_path] + self.cmd_args,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout_data, stderr_data) = program.communicate(
            input=self.json_request)
        self._done = True        

        # check return code:
        exit_code = program.poll()
        if exit_code != 0:
            logging.debug("[client.api.NodeAction] exit code " +\
                str(exit_code) + " (failure)")
            # convert stderr from bytes to string if necessary:
            try:
                stderr_data = stderr_data.decode("utf-8", "ignore")
            except AttributeError:
                pass
            return (False, "the process returned non-zero exit code " +\
                str(exit_code) + " with the following stderr output: " +\
                stderr_data)
        else:
            logging.debug("[client.api.NodeAction] exit code 0 (success)")

        # convert result from bytes to string if necessary:
        try:
            stdout_data = stdout_data.decode("utf-8", "ignore")
        except AttributeError:
            pass

        # convert response to JSON:
        if self.answer_is_json:
            try:
                json_obj = json.loads(stdout_data)
            except ValueError:
                return (False, stdout_data)
            return (True, json_obj)
        return (True, stdout_data)

    @property
    def done(self):
        return self._done 


