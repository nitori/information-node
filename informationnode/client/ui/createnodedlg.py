
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
        self.node_location_entry.set_text(self.get_suggested_new_node_path())
        vbox.add(
            uilib.Label("This location will contain all the node's "+\
            "stored data and such.\nIt should be an empty or " +\
            "new folder.", line_breaks=True)).set_alignment(0, 0.5)

        self.set_modal(True)
        vbox.show_all()

    def get_filename(self):
        return self.node_location_entry.get_text()

    def get_suggested_new_node_path(self):
        home_dir = os.path.expanduser("~")
        number = 0
        base_path = os.path.join(home_dir, "my_new_node")
        path = base_path
        while os.path.exists(path):
            number += 1
            path = base_path + "_" + str(number)
        return path

    def run(self):
        result = super(CreateNodeDialog, self).run()
        return result

