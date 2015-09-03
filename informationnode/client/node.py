
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

from enum import Enum
from informationnode.helper import check_if_node_dir, check_if_node_runs
import logging
import os
import sys
import time

class NodeState(Enum):
    UNKNOWN=0
    DATA_SERVER_OFF=1
    DATA_SERVER_ON=2
    DATA_SERVER_UNREACHABLE=3
    INVALID_STATE=4

class Node(object):
    """ The model which manages a node at a specific directory through a
        connection to the node's data server. Used by the client UI to
        represent and manage a node.

        The node will be immediately opened or created in the constructor, so
        expect the instance creation to hang for a while (up to ~20 seconds).

        Other operations can hang as well until the respective required
        communication with the node data server has finished.
    """
    def __init__(self, app, path, create_new=False):
        """ Constructor for the node. Expect it to hang for a while in some
            cases (especially node creation can take a while).

            Errors raised by the constructor:

            Raises a ValueError if the given location is not a valid node.
            Raises a RuntimeError if opening or creating the node fails for some
            unexpected reason.
        """
        super().__init__()

        self.app = app
        self.state = NodeState.UNKNOWN
        self.path = path

        # see if this is a valid node:
        (result, msg) = check_if_node_dir(path)
        if not result and not create_new:
            raise ValueError("not an accessible information node: " +\
                str(msg)) 
        elif result and create_new:
            raise ValueError("information node already exists, cannot " +\
                "create here")

        # create node if necessary:
        if create_new:
            (result, content) = self._create() 
            if not result:
                raise RuntimeError("information node creation failed: " +\
                    str(content))

        # detect the node state.
        self._detect_state()

    def can_use(self):
        """ Check if this node is in any usable state. If not, you will either
            need to launch the data server or have the user fix it before you
            can perform any other advanced actions on it.
        """
        self._detect_state()
        if self.state != NodeState.DATA_SERVER_ON:
            return False
        return True

    def launch_data_server(self):
        """ If the state of the node is NodeState.DATA_SERVER_OFF, call this
            to launch the data server.

            Return value: (result, errmsg)
            Returns a tuple with the result which can be True or False, and
            an error message if things went wrong (result = False).
        """
        if self.state != NodeState.DATA_SERVER_OFF:
            raise RuntimeError("not in data server off state, cannot launch")
        action = self.app.actions.do(
            self.path, "", tool="information-node",
            cmd="node", answer_is_json=False)
        (result, content) = action.run()
        if result:
            self.state = NodeState.UNKNOWN
            self._detect_state()
        return (result, content)

    def _check_node_data_server(self, force_recheck=False):
        """ Internal function which checks the state of the data server. The
            data server will be pinged if it appears to be running to make
            sure it is reachable, unless this has already been done before.

            To force another ping to make sure it is still reachable right
            now, use force_recheck = True.
        """
        if self.state == NodeState.DATA_SERVER_ON and not force_recheck:
            return

        # check if there's a data server process:
        (result, msg) = check_if_node_runs(self.path)
        if result == None:
            self.state = NodeState.INVALID_STATE
            return
        if result != True:
            self.state = NodeState.DATA_SERVER_OFF
            return

        # ping the data server:
        action = self.app.actions.do(
            self.path, "", cmd="ping")
        (result, content) = action.run()
        if not result:
            self.state = NodeState.DATA_SERVER_UNREACHABLE
        else:
            self.state = NodeState.DATA_SERVER_ON

    def _detect_state(self):
        """ Internal function to detect/update the node's state.
        """
        # check for detailed data server state if necessary:
        if self.state == NodeState.UNKNOWN:
            self._check_node_data_server()
       
    def _create(self): 
        """ Internal function to create this new node on the disk in the given
            path.
        """
        action = self.app.actions.do(
            self.path, "", tool="information-node",
            cmd="node", answer_is_json=False)
        (result, content) = action.run()
        return (result, content)

    def __del__(self):
        self._detect_state()

        # clean up:

        pass


