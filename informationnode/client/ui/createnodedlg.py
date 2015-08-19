
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

from gi.repository import Gtk
from informationnode.helper import check_if_node_dir, check_if_node_runs
import informationnode.uilib as uilib
import os
import sys

class CreateNodeDialog(uilib.Dialog):
    def __init__(self, parent=None):
        super(CreateNodeDialog, self).__init__(title="Create New Node",
            parent=parent,
            buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OK, Gtk.ResponseType.OK))
        vbox = uilib.VBox()
        self.vbox.pack_start(vbox, True, True, 0)

        self.vbox.set_property("margin", 10)
        vbox.add(uilib.Label("Specify the location for your new node:")).\
            set_alignment(0, 0.5)
        self.node_location_entry = vbox.add(uilib.TextEntry())
        vbox.add(
            uilib.Label("This location will contain all the node's "+\
            "stored data and such.")).set_alignment(0, 0.5)

        self.set_modal(True)
        vbox.show_all()

    def run(self):
        result = super(CreateNodeDialog, self).run()
        return result

