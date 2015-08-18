
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

from gi.repository import Gtk
from informationnode.helper import check_if_node_dir, check_if_node_runs
import informationnode.uilib as uilib
import os
import sys

class CreateNodeWindow(uilib.Window):
    def __init__(self):
        super(CreateNodeWindow, self).__init__()
        self.box.set_property("margin", 10)
        self.add(uilib.Label("Specify the location for your new node:"),
            padding=10).\
            set_alignment(0, 0.5)
        self.node_location_entry = self.add(uilib.TextEntry())
        self.add(uilib.Label("This location will contain all the node's "+\
            "stored data and such.")).set_alignment(0, 0.5)
        self.set_title("Create Node")
        self.set_modal(True)

