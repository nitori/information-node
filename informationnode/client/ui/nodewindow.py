
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
from gi.repository import Gtk
from informationnode.helper import check_if_node_dir, check_if_node_runs
import informationnode.uilib as uilib
from informationnode.client.ui.createnodedlg import CreateNodeDialog
from informationnode.client.ui.viewerlogwindow import ViewerLogWindow
import os
import sys
import time

class NodeState(Enum):
    UNKNOWN=0
    DATA_SERVER_OFF=1
    DATA_SERVER_ON=2
    DATA_SERVER_UNREACHABLE=3

class NodeWindow(uilib.Window):
    def __init__(self, app, node_path):
        super().__init__()

        self.app = app

        self.node_state = NodeState.UNKNOWN
        self.node_path = node_path
        self.menu = self.build_menu()
        self.add(self.menu)
        self.notebook = self.build_notebook()
        self.add(self.notebook, expand=True)

        self.detect_node_state()
        self.node_state_popup()

    def node_state_popup(self):
        if self.node_path != None:
            if self.node_state == NodeState.DATA_SERVER_OFF:
                if uilib.Dialog.show_yesno(
                        "This node's data server is not running. Launch it?",
                        "Data server is off"):
                    action = self.app.actions.do(
                        self.node_path, "", tool="information-node",
                        cmd="node", answer_is_json=False)
                    (result, content) = action.run()
                    if not result:
                        uilib.Dialog.show_error(
                            "Launching the data server failed: " +\
                             str(content),
                            "Failed to launch data server", parent=self)
                        self.node_path = None
                        self.node_state = NodeState.UNKNOWN
                        self.detect_node_state()
                        return
                    self.node_state = NodeState.UNKNOWN
                    self.detect_node_state()
                    self.node_state_popup()
                else:
                    self.node_path = None
                    self.node_state = NodeState.UNKNOWN
                    self.detect_node_state()
            elif self.node_state == NodeState.DATA_SERVER_UNREACHABLE:
                uilib.Dialog.show_error( # FIXME TEXT
                    "Cannot use this node, data server is unreachable. " +\
                    "Try terminating and restarting the data server.",
                    parent=self)
                self.node_path = None
                self.node_state = NodeState.UNKNOWN
                self.detect_node_state()
            elif self.node_state != NodeState.DATA_SERVER_ON:
                uilib.Dialog.show_error(
                    "Cannot use this node, data server was " +\
                    "detected in unknown state: " + str(self.node_state),
                    "Data server in unknown state", parent=self)
                self.node_path = None
                self.node_state = NodeState.UNKNOWN
                self.detect_node_state()

    def show_long_action_notice(self,
            operation="This might take a moment..."):
        if hasattr(self, "long_action_win") and \
                self.long_action_win != None:
            return
        win = uilib.Window()
        win.set_title("Please be patient...")
        win.set_transient_for(self)

        vbox = uilib.VBox()
        win.add(vbox)
        
        vbox.add(uilib.Label(operation))

        def no_delete(self, *args):
            return True 

        win.connect('delete_event', no_delete)
        win.show_all()
        
        # make sure the window shows:
        t = time.time()
        while time.time() < t+1:
            while Gtk.events_pending():
                Gtk.main_iteration()

        self.long_action_win = win

    def hide_long_action_notice(self):
        if not hasattr(self, "long_action_win") or \
                not self.long_action_win != None:
            return
        self.long_action_win.destroy()

    def check_node_data_server(self):
        # check if there's a data server process:
        (result, msg) = check_if_node_runs(self.node_path)
        if result == None:
            uilib.Dialog.show_error(
                "Node has invalid state: " + str(msg),
                "Error when checking node state",
                parent=self)
            self.node_path = None
            return
        if result != True:
            self.node_state = NodeState.DATA_SERVER_OFF
            return

        # ping the data server:
        action = self.app.actions.do(
            self.node_path, "", cmd="ping")
        (result, content) = action.run()
        if not result:
            self.node_state = NodeState.DATA_SERVER_UNREACHABLE
        else:
            self.node_state = NodeState.DATA_SERVER_ON

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

        # add second vertical spacer:
        new_tab_box.add(uilib.VBox(), end=False, expand=True, fill=True)

        return notebook

    def detect_node_state(self):
        """ Change this node window's entire state based on whether it has
            currently a node opened or not, and detect the detailed state.
        """
        opened = (self.node_path != None)

        # check for detailed data server state if necessary:
        if opened:
            if self.node_state == NodeState.UNKNOWN:
                self.check_node_data_server()
        
        # adapt window/menus to reflect the state:
        if opened and self.node_path != None:
            self.menu.nodemenu.close.enable()
            self.menu.logmenu.dataserver.enable()
            self.set_title("Node: " + self.node_path)
        else:
            self.menu.nodemenu.close.disable()
            self.menu.logmenu.dataserver.disable()
            self.set_title("Information Node Viewer")

    def nodemenu_open_remote(self, widget):
        print("TEST")        

    def nodemenu_create(self, widget):
        create_win = CreateNodeDialog()
        create_win.set_transient_for(self)
        result = create_win.run()
        fpath = None
        if result == Gtk.ResponseType.OK:
            fpath = create_win.get_filename()
        create_win.destroy()

        # create new node if instructed to:
        if fpath != None:
            self.show_long_action_notice(
                "Creating a new information node...")
            action = self.app.actions.do(
                fpath, "", tool="information-node",
                cmd="node", answer_is_json=False)
            (result, content) = action.run()
            self.hide_long_action_notice()
            if not result:
                uilib.Dialog.show_error(
                    "The node creation failed: " + str(content),
                    "Failed to create node", parent=self)
            else:
                if self.node_path == None:
                    # this window has no node opened, open it in here
                    self.node_path = fpath
                    self.detect_node_state()
                    self.node_state_popup()
                else:
                    # open it in a new window:
                    new_win = NodeWindow(self.app, fpath)
                    self.app.add_window(new_win)

    def nodemenu_close(self, widget):
        if self.node_path == None:
            return
        self.node_path = None
        self.detect_node_state()    

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

            # open the node up:
            if self.node_path == None:
                # this window has no node opened, open it in here
                self.node_path = directory
                self.detect_node_state()
                self.node_state_popup()
            else:
                # open it in a new window:
                new_win = NodeWindow(self.app, directory)
                self.app.add_window(new_win)
            
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

        # log menu contents:
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


