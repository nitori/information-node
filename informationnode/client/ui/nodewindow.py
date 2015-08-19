
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
from informationnode.client.ui.createnodedlg import CreateNodeDialog
from informationnode.client.ui.viewerlogwindow import ViewerLogWindow
import os
import sys

class NodeWindow(uilib.Window):
    def __init__(self, app, node_path):
        super().__init__()

        self.app = app

        if node_path == None:
            self.set_title("Information Node Viewer")
        else:
            self.set_title("Information Node: " + node_path)
        
        self.node_path = node_path
        self.menu = self.build_menu()
        self.add(self.menu)
        self.notebook = self.build_notebook()
        self.add(self.notebook, expand=True)

        self.set_node_opened(False)    

    def build_notebook(self):
        notebook = uilib.Notebook()
        
        # add tab:
        new_tab_contents = uilib.HBox()
        notebook.add(new_tab_contents, "Welcome")

        # add first horizontal spacer
        new_tab_contents.add(uilib.HBox(), end=False, expand=True, fill=True)
 
        # add vbox into hbox, centered:
        new_tab_box = uilib.VBox(spacing=5)
        new_tab_contents.add(new_tab_box, expand=False)

        # add first vertical spacer:
        new_tab_box.add(uilib.VBox(), end=False, expand=True, fill=True)

        new_tab_box.add(uilib.Label("Welcome! Choose what to do:"))
        self.welcome_tab_recent_node = new_tab_box.add(
            uilib.RadioButton(
            "Open recently opened node:"))
        self.welcome_tab_recent_node.disable()
        self.welcome_tab_open_node_disk = new_tab_box.add(
            uilib.RadioButton(
            "Open local node...",
            group=self.welcome_tab_recent_node))
        self.welcome_tab_open_node_disk.set_active(True)
        self.welcome_tab_open_node_remote = new_tab_box.add(
            uilib.RadioButton(
            "Open remote node...",
            group=self.welcome_tab_open_node_disk))
        self.welcome_tab_create_node = new_tab_box.add(
            uilib.RadioButton("Create a new node",
            group=self.welcome_tab_open_node_remote))

        # add second horizontal spacer:
        new_tab_contents.add(uilib.HBox(), end=False, expand=True, fill=True)

        # add button box:
        button_hbox = uilib.HBox()
        new_tab_box.add(button_hbox, end=False)

        # add "Go!" button:
        do_it = uilib.Button("Go!")
        do_it.register("click", lambda button: self.welcometab_go())
        button_hbox.add(do_it, fill=True, expand=True)

        # add second vertical sapcer:
        new_tab_box.add(uilib.VBox(), end=False, expand=True, fill=True)

        return notebook

    def set_node_opened(self, opened):
        if opened:
            self.menu.nodemenu.close.enable()
        else:
            self.menu.nodemenu.close.disable()

    def nodemenu_open(self, widget):
        print("TEST")

    def nodemenu_open_remote(self, widget):
        print("TEST")        

    def nodemenu_create(self, widget):
        create_win = CreateNodeDialog()
        create_win.set_transient_for(self)
        result = create_win.run()
        create_win.destroy()

    def nodemenu_close(self, widget):
        print("TEST")    

    def nodemenu_quit(self, widget):
        sys.exit(0)

    def logmenu_viewerlog(self, widget):
        self.app.add_window(ViewerLogWindow(self.app))

    def welcometab_go(self):
        if self.welcome_tab_open_node_disk.get_active():
            self.nodemenu_open(None)
        elif self.welcome_tab_create_node.get_active():
            self.nodemenu_create(None)

    def nodemenu_open(self, widget):
        dlg = Gtk.FileChooserDialog("Open up Information Node",
            self, Gtk.FileChooserAction.SELECT_FOLDER,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        response = dlg.run()
        if response == Gtk.ResponseType.OK:
            directory = dlg.get_filename()
            dlg.destroy()
            print("SHOW OPEN DIALOG: " + str(directory))

            # see if this is a valid node:
            (result, msg) = check_if_node_dir(directory)
            if not result:
                dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.OK,
                    "Cannot access node")
                dialog.format_secondary_text(
                    "Cannot access the specified node: " + str(msg))
                dialog.run()
                dialog.destroy()
                return

        else:
            dlg.destroy()

    def aboutmenu_about(self, widget):
        about = uilib.AboutDialog()
        about.set_program_name("Information Node Viewer")
        about.set_copyright(
            "(C) 2015 Information Node Development Team")
        about.set_website(
            "https://github.com/information-node/information-node")
        about.set_version("0.1")
        about.set_comments("Universal data synchronization software")

        # load up and embed authors list:
        try:
            import pkg_resources
            authors = pkg_resources.resource_string("informationnode",
                os.path.join("data", "AUTHORS.md")).decode("utf-8", "ignore")
        except FileNotFoundError:
            authors = open(os.path.join(os.path.dirname(__file__),
                "..", "..", "..", "AUTHORS.md"),
                "r").read()  # go up from inode.client.ui
        authors = [l[1:].strip() for l in authors.splitlines() \
            if l.startswith("-")]
        about.set_authors(authors)

        # load up and embed license:
        try:
            import pkg_resources
            license = pkg_resources.resource_string("informationnode",
                os.path.join("data", "LICENSE.txt")).decode("utf-8", "ignore")
        except FileNotFoundError:
            license = open(os.path.join(os.path.dirname(__file__),
                "..", "..", "..", "LICENSE.txt"),
                "r").read()  # go up from inode.client.ui
        about.set_license(license)

        about.run()
        about.destroy()

    def build_menu(self):
        menu = uilib.MenuBar()

        # add node menu:        
        menu.nodemenulabel = uilib.MenuItem("_Node")
        menu.add(menu.nodemenulabel)
        menu.nodemenu = uilib.Menu()
        menu.nodemenulabel.add(menu.nodemenu)

        # node menu contents:
        menu.nodemenu.open = uilib.MenuItem("_Open Local Node...")
        menu.nodemenu.open.register("click",
            self.nodemenu_open)
        menu.nodemenu.add(menu.nodemenu.open)
        menu.nodemenu.open_remote = uilib.MenuItem(
            "Connect To _Remote Node...")
        menu.nodemenu.open_remote.register("click",
            self.nodemenu_open_remote)
        menu.nodemenu.add(menu.nodemenu.open_remote)
        menu.nodemenu.add(uilib.SeparatorMenuItem())
        menu.nodemenu.create = uilib.MenuItem("Create _New Node...")
        menu.nodemenu.create.register("click",
            self.nodemenu_create)
        menu.nodemenu.add(menu.nodemenu.create)
        menu.nodemenu.add(uilib.SeparatorMenuItem())
        menu.nodemenu.close = uilib.MenuItem("_Close Current Node")
        menu.nodemenu.close.register("click",
            self.nodemenu_close)
        menu.nodemenu.add(menu.nodemenu.close)
        menu.nodemenu.add(uilib.SeparatorMenuItem())
        menu.nodemenu.quit = uilib.MenuItem("_Quit")
        menu.nodemenu.quit.register("click",
            self.nodemenu_quit)
        menu.nodemenu.add(menu.nodemenu.quit)

        # add log menu:
        menu.logmenulabel = uilib.MenuItem("_Log")
        menu.add(menu.logmenulabel)
        menu.logmenu = uilib.Menu()
        menu.logmenulabel.add(menu.logmenu)

        # node log contents:
        menu.logmenu.dataserver = uilib.MenuItem("Show Node _Data Server Log")
        #menu.logmenu.dataserver.register("click",
        #    self.nodemenu_open)
        menu.logmenu.add(menu.logmenu.dataserver)
        menu.logmenu.viewerlog = uilib.MenuItem(
            "Show _Viewer Activity Log")
        menu.logmenu.viewerlog.register("click",
            self.logmenu_viewerlog)
        menu.logmenu.add(menu.logmenu.viewerlog)
 
        # add about menu:        
        menu.aboutmenulabel = uilib.MenuItem("_About")
        menu.add(menu.aboutmenulabel)
        menu.aboutmenu = uilib.Menu()
        menu.aboutmenulabel.add(menu.aboutmenu)

        # node menu contents:
        menu.aboutmenu.about = uilib.MenuItem(
            "_About Information Node Viewer...")
        menu.aboutmenu.about.register("click",
            self.aboutmenu_about)
        menu.aboutmenu.add(menu.aboutmenu.about)
 
        return menu


