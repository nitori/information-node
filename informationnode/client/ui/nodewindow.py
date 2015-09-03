
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
from informationnode.client.node import Node, NodeState
from informationnode.client.ui.createnodedlg import CreateNodeDialog
from informationnode.client.ui.viewerlogwindow import ViewerLogWindow
import logging
import os
import sys
import time

logging.basicConfig(level=logging.DEBUG)

class NodeWindow(uilib.Window):
    def __init__(self, app, node):
        super().__init__()

        self.app = app

        self.node_state = NodeState.UNKNOWN
        self.node = node

        self.menu = self.build_menu()
        self.add(self.menu)
        
        self.build_notebook()

        self.update_node_state()
        self.node_state_popup()

    def node_state_popup(self):
        if self.node != None and not self.node.can_use():
            if self.node.state == NodeState.DATA_SERVER_OFF:
                if uilib.Dialog.show_yesno(
                        "This node's data server is not running. Launch it?",
                        title="Data server is off"):
                    (result, content) = self.node.launch_data_server()
                    if not result:
                        uilib.Dialog.show_error(
                            "Launching the data server failed: " +\
                             str(content),
                            "Failed to launch data server", parent=self)
                        self.update_node_state()
                        return
                    self.update_node_state()
                    self.node_state_popup()
                    return
            elif self.node.state == NodeState.DATA_SERVER_UNREACHABLE:
                uilib.Dialog.show_error( # FIXME TEXT
                    "Cannot use this node, data server is unreachable. " +\
                    "Try terminating and restarting the data server.",
                    parent=self)
                self.update_node_state()
            else:
                uilib.Dialog.show_error(
                    "Cannot use this node, data server was " +\
                    "detected in unknown state: " + str(self.node_state),
                    "Data server in unknown state", parent=self)

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

    def build_notebook(self):
        if self.node == None:
            self.notebook = self.build_welcome_notebook()
        else:
            self.notebook = self.build_node_notebook()
        self.add(self.notebook, expand=True)
        self.notebook.show_all()
        self.notebook_update_usable_state()

    def rebuild_notebook(self):
        self.destroy_notebook()
        assert(not hasattr(self, "notebook"))
        self.build_notebook()

    def notebook_update_usable_state(self):
        if self.node == None:
            return
        can_use = self.node.can_use()    
        pass

    def destroy_notebook(self):
        if not hasattr(self, "notebook"):
            # nothing to do
            return

        # helper function to get rid of widgets stored as members:
        def destroy_widgets_which_are_members(widget):
            for attr in dir(widget):
                if attr.startswith("__"):
                    continue
                try:
                    member = getattr(widget, attr)
                except RuntimeError:
                    continue
                if hasattr(member, "destroy"):
                    try:
                        member.destroy()
                    except Exception as e:
                        pass

        logging.debug("[nodewindow] Destroying notebook widget")
        self.remove(self.notebook)
        if hasattr(self, "welcome_tab"):
            destroy_widgets_which_are_members(self.welcome_tab)
            self.welcome_tab.destroy()
            del(self.welcome_tab)
        elif hasattr(self, "conversations_tab"):
            def destroy_tab(name):
                tab = getattr(self, name)
                destroy_widgets_which_are_members(tab)
                tab.destroy()
                delattr(self, name)
                assert(not hasattr(self, name))
            destroy_tab("conversations_tab")
            destroy_tab("files_tab")
            destroy_tab("gateways_tab")
        self.notebook.destroy()
        del(self.notebook)

    def build_node_notebook(self):
        logging.debug("[nodewindow] Building node notebook contents")
        notebook = uilib.Notebook()       

        # add "Conversations" tab:
        self.conversations_tab = uilib.HBox()
        notebook.add(self.conversations_tab, "Conversations")

        # add "Files" tab:
        self.files_tab = uilib.HBox()
        notebook.add(self.files_tab, "Files")

        # add "Gateways" tab:
        self.gateways_tab = uilib.HBox()
        notebook.add(self.gateways_tab, "Gateways")

        # add "Synchronization" tab:
        self.synchronization_tab = uilib.HBox()
        notebook.add(self.synchronization_tab, "Synchronization")

        # add "Status" tab:
        self.status_tab = uilib.HBox()
        notebook.add(self.status_tab, "Status")

        return notebook

    def build_welcome_notebook(self):
        logging.debug("[nodewindow] Building welcome notebook contents")
        notebook = uilib.Notebook()
        
        # add "welcome" tab:
        self.welcome_tab = uilib.HBox()
        notebook.add(self.welcome_tab, "Welcome")

        # add first horizontal spacer
        self.welcome_tab.add(uilib.HBox(), end=False, expand=True, fill=True)
 
        # add vbox into hbox, centered:
        new_tab_box = uilib.VBox(spacing=5)
        self.welcome_tab.add(new_tab_box, expand=False)

        # add first vertical spacer:
        new_tab_box.add(uilib.VBox(), end=False, expand=True, fill=True)

        new_tab_box.add(uilib.Label("Welcome! Choose what to do:"))
        self.welcome_tab.recent_node = new_tab_box.add(
            uilib.RadioButton(
            "Open recently opened node:"))
        self.welcome_tab.recent_node.disable()
        self.welcome_tab.open_node_disk = new_tab_box.add(
            uilib.RadioButton(
            "Open local node...",
            group=self.welcome_tab.recent_node))
        self.welcome_tab.open_node_disk.set_active(True)
        #self.welcome_tab.open_node_remote = new_tab_box.add(
        #    uilib.RadioButton(
        #    "Open remote node...",
        #    group=self.welcome_tab.open_node_disk))
        self.welcome_tab.create_node = new_tab_box.add(
            uilib.RadioButton("Create a new node",
            group=self.welcome_tab.open_node_disk))

        # add second horizontal spacer:
        self.welcome_tab.add(uilib.HBox(), end=False, expand=True, fill=True)

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

    def update_node_state(self):
        """ Change this node window's entire state based on whether it has
            currently a node opened or not, and whether the node can be used
            right now.
        """
        opened = (self.node != None)

        previously_opened = True
        if hasattr(self, "welcome_tab"):
            previously_opened = False

        previously_usable = False
        if self.menu.logmenu.dataserver.enabled():
            previously_usable = True

        # adapt window/menus to reflect the state:
        if opened:
            can_use = self.node.can_use()
            self.menu.nodemenu.close.enable()
            if can_use:
                self.menu.logmenu.dataserver.enable()
            else:
                self.menu.logmenu.dataserver.disable()
            self.set_title("Node: " + self.node.path + (\
                " [Disconnected]" if not can_use else ""))
        else:
            self.menu.nodemenu.close.disable()
            self.menu.logmenu.dataserver.disable()
            self.set_title("Information Node Viewer")
        
        # rebuild notebook if necessary:
        if previously_opened != opened:
            self.rebuild_notebook()

        # update notebook usable state:
        if opened and previously_opened:
            if previously_usable != self.node.can_use():
                self.notebook_update_usable_state()

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
            try:
                node = Node(self.app, fpath, create_new=True)
            except (RuntimeError, ValueError) as e:
                uilib.Dialog.show_error(
                    "The node creation failed: " + str(e),
                    "Failed to create node", parent=self)
            else:
                if self.node == None:
                    # this window has no node opened, open it in here
                    self.node = node
                    self.update_node_state()
                    self.node_state_popup()
                else:
                    # open it in a new window:
                    new_win = NodeWindow(self.app, node)
                    self.app.add_window(new_win)

    def nodemenu_close(self, widget):
        if self.node == None:
            return
        del(self.node)
        self.node = None
        self.update_node_state()    

    def nodemenu_quit(self, widget):
        sys.exit(0)

    def logmenu_viewerlog(self, widget):
        self.app.add_window(ViewerLogWindow(self.app))

    def welcometab_go(self):
        if self.welcome_tab.open_node_disk.get_active():
            self.nodemenu_open(None)
        elif self.welcome_tab.create_node.get_active():
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
            try:
                node = Node(self.app, directory)
            except (RuntimeError, ValueError) as e:
                dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.OK,
                    "Cannot access node")
                dialog.format_secondary_text(
                    "Cannot access the specified node: " + str(e))
                dialog.run()
                dialog.destroy()
                return

            if self.node == None:
                # this window has no node opened, open it in here
                self.node = node
                self.update_node_state()
                self.node_state_popup()
            else:
                # open it in a new window:
                new_win = NodeWindow(self.app, node)
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
        #menu.nodemenu.open_remote = uilib.MenuItem(
        #    "Connect To _Remote Node...")
        #menu.nodemenu.open_remote.register("click",
        #    self.nodemenu_open_remote)
        #menu.nodemenu.add(menu.nodemenu.open_remote)
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


