
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
from informationnode.client.ui.createnodedlg import CreateNodeDialog
import os
import sys

class ViewerLogWindow(uilib.Window):
    def __init__(self, app):
        super().__init__()

        self.set_default_size(550, 550)

        self.set_title("Viewer Activity Log")
        self.app = app

        vbox = uilib.VBox()
        vbox.set_property("margin", 10)
        self.add(vbox)

        vbox.add(uilib.Label("Due to the sensitive nature of this log, " +\
            "it needs to be enabled using --debug-history.\nIt will "+\
            "only be stored in memory until the viewer quits, not on disk.",
            line_breaks=True))\
            .set_alignment(0, 0.5)

        hbox = uilib.HBox()
        hbox.add(uilib.Label("Show activity for node:")).\
            set_alignment(0, 0.5)
        self.node_choice = hbox.add(uilib.ComboBoxText())
        self.node_choice.append_text("No tracked past activity with any node")
        self.node_choice.set_active(0)
        self.node_choice.disable()

        vbox.add(hbox)
