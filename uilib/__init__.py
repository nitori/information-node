
from gi.repository import Gtk
import os
import platform

def uilib_main_loop():
    """ Launches the main event loop. Doesn't return until the program is
        terminated.
     """
    Gtk.main()

def uilib_quit():
    Gtk.main_quit()

if platform.system().lower() != "windows":
    import signal
    def sigint_handler(_ignore_1, _ignore_2):
        os._exit(0)
    #signal.signal(signal.SIGINT, sigint_handler)
    signal.signal(signal.SIGINT, signal.SIG_DFL)

class WidgetMixin(object):
    def register(self, event, callback):
        """ Known events:
            "click",
            "close" (for windows)
        """
        if not hasattr(self, "callbacks"):
            self.callbacks = dict()
        if not (event in self.callbacks):
            self.callbacks[event] = []
        self.callbacks[event].append(callback)

    def trigger(self, event):
        if not hasattr(self, "callbacks"):
            return False
        if not (event in self.callbacks):
            return False
        for callback in self.callbacks[event]:
            v = callback(self)
            if v == True:
                return True
        return False

class Window(Gtk.Window, WidgetMixin):
    def __init__(self):
        super(Window, self).__init__()
        self.box = Gtk.VBox()
        self.connect("delete-event", lambda ignore1, ignore2: \
            self._close_event())
        super(Window, self).add(self.box)

    def _close_event(self):
        self.trigger("close")

    def add(self, widget, expand=False):
        if expand:
            self.box.pack_start(widget, True, True, 0)
        else:
            self.box.pack_start(widget, False, False, 0)

    def show(self):
        self.show_all()

class VBox(Gtk.VBox, WidgetMixin):
    def __init__(self, spacing=0):
        super(VBox, self).__init__(spacing=spacing)

    def add(self, widget, expand=False):
        if expand:
            self.pack_start(widget, True, True, 0)
        else:
            self.pack_start(widget, False, False, 0)

class HBox(Gtk.HBox, WidgetMixin):
    def __init__(self, spacing=0):
        super(HBox, self).__init__(spacing=spacing)

    def add(self, widget, expand=False):
        if expand:
            self.pack_start(widget, True, True, 0)
        else:
            self.pack_start(widget, False, False, 0)

class TextEntry(Gtk.Entry, WidgetMixin):
    def __init__(self, text=""):
        super(TextEntry, self).__init__()
        self.set_text(text)

class Menu(Gtk.Menu, WidgetMixin):
    def add(self, menu_entry):
        if not isinstance(menu_entry, MenuItem) and \
                not isinstance(menu_entry, SeparatorMenuItem):
            raise RuntimeError("Menu doesn't support adding " +\
                "arbitrary kind of widgets, " +\
                "just MenuItem widgets are allowed")
        super(Menu, self).append(menu_entry)

class MenuItem(Gtk.MenuItem, WidgetMixin):
    def __init__(self, text=""):
        super(MenuItem, self).__init__(label=text)

    def set_text(self, text):
        self.remove(self._label)
        self._label.destroy()
        self._label = Gtk.Label(text)
        super(MenuItem, self).add(self._label)

    def add(self, menu):
        if not isinstance(menu, Menu):
            raise RuntimeError("MenuItem doesn't support adding " +\
                "arbitrary kind of widgets, " +\
                "just Menu widgets are allowed")
        super(MenuItem, self).set_submenu(menu)

class SeparatorMenuItem(Gtk.SeparatorMenuItem, WidgetMixin):
    def add(self, menu):
        if not isinstance(menu, MenuItem):
            raise RuntimeError("MenuItem doesn't support adding " +\
                "arbitrary kind of widgets, " +\
                "just Menu widgets are allowed")
        super(MenuItem, self).set_submenu(menu)

class MenuBar(Gtk.MenuBar, WidgetMixin):
    def add(self, menu_entry):
        if not isinstance(menu_entry, MenuItem):
            raise RuntimeError("MenuBar doesn't support adding " +\
                "arbitrary kind of widgets, " +\
                "just MenuItem widgets are allowed")
        self.append(menu_entry)       

class Label(Gtk.Label, WidgetMixin):
    pass
        
class Notebook(Gtk.Notebook, WidgetMixin):
    def __init__(self, *args, **kwargs):
        super(Notebook, self).__init__(*args, **kwargs)
        self.new_tab_id = 0

    def add(self, tab_widget, tab_title=None):
        if tab_title == None:
            self.new_tab_id += 1
            tab_title = "Tab " + str(self.new_tab_id)
        label = Gtk.Label(label=tab_title)
        self.append_page(tab_widget, label)

