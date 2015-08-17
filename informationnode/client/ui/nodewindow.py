
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
import uilib

class NodeWindow(uilib.Window):
    def __init__(self, node_path):
        super().__init__()

        if node_path == None:
            self.set_title("Information Node Viewer")
        else:
            self.set_title("Information Node: " + node_path)
        
        self.node_path = node_path
        self.menu = self.build_menu()
        self.add(self.menu)
        self.notebook = self.build_notebook()
        self.add(self.notebook, expand=True)
    
    def build_notebook(self):
        notebook = uilib.Notebook()
        
        # add tab:
        new_label = uilib.Label("Welcome tab contents")
        notebook.add(new_label, "Welcome")
        
        return notebook

    def nodemenu_open(self):
        print("TEST")
        
    def nodemenu_create(self):
        print("TEST")
    
    def aboutmenu_about(self):
        pass
        
    def build_menu(self):
        menu = uilib.MenuBar()

        # add node menu:        
        menu.nodemenulabel = uilib.MenuItem("Node")
        menu.add(menu.nodemenulabel)
        menu.nodemenu = uilib.Menu()
        menu.nodemenulabel.add(menu.nodemenu)

        # node menu contents:
        menu.nodemenu.open = uilib.MenuItem("Open node...")
        menu.nodemenu.open.register("click",
            self.nodemenu_open)
        menu.nodemenu.add(menu.nodemenu.open)
        menu.nodemenu.add(uilib.SeparatorMenuItem())
        menu.nodemenu.create = uilib.MenuItem("Create new node...")
        menu.nodemenu.create.register("click",
            self.nodemenu_create)
        menu.nodemenu.add(menu.nodemenu.create)
        menu.nodemenu.add(uilib.SeparatorMenuItem())
        menu.nodemenu.quit = uilib.MenuItem("Quit")
        menu.nodemenu.add(menu.nodemenu.quit)
        
        # add about menu:        
        menu.aboutmenulabel = uilib.MenuItem("About")
        menu.add(menu.aboutmenulabel)
        menu.aboutmenu = uilib.Menu()
        menu.aboutmenulabel.add(menu.aboutmenu)

        # node menu contents:
        menu.aboutmenu.about = uilib.MenuItem(
            "About information node viewer...")
        menu.aboutmenu.about.register("click",
            self.aboutmenu_about)
        menu.aboutmenu.add(menu.aboutmenu.about)
 
        return menu
    pass

