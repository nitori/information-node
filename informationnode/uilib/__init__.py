
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

    def enable(self):
        self.set_sensitive(True)

    def disable(self):
        self.set_sensitive(False)

class Window(Gtk.Window, WidgetMixin):
    def __init__(self):
        super(Window, self).__init__()
        self.box = Gtk.VBox()
        self.connect("delete-event", lambda ignore1, ignore2: \
            self.trigger("close"))
        super(Window, self).add(self.box)

    def add(self, widget, expand=False, padding=5):
        if expand:
            self.box.pack_start(widget, True, True, padding)
        else:
            self.box.pack_start(widget, False, False, padding)
        return widget

    def remove(self, widget):
        self.box.remove(widget)

    def show(self):
        self.show_all()

class AddInsteadOfPackMixin(object):
    def add(self, widget, expand=False, end=False, fill=None, padding=5):
        if fill == None:
            fill = expand
        if not end:
            if expand:
                self.pack_start(widget, True, fill, padding=padding)
            else:
                self.pack_start(widget, False, fill, padding=padding)
        else:
            if expand:
                self.pack_start(widget, True, fill, padding=padding)
            else:
                self.pack_start(widget, False, fill, padding=padding)
        return widget

class VBox(AddInsteadOfPackMixin, Gtk.VBox, WidgetMixin):
    def __init__(self, spacing=0):
        super(VBox, self).__init__(spacing=spacing)

class HBox(AddInsteadOfPackMixin, Gtk.HBox, WidgetMixin):
    def __init__(self, spacing=0):
        super(HBox, self).__init__(spacing=spacing)

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
        return menu_entry

class MenuItem(Gtk.MenuItem, WidgetMixin):
    def __init__(self, text=""):
        super(MenuItem, self).__init__(label=text)
        self.set_text(text)
        self.connect("activate", lambda button: self.trigger("click"))

    def set_text(self, text):
        self.set_use_underline(True)
        super(MenuItem, self).set_label(text)

    def add(self, menu):
        if not isinstance(menu, Menu):
            raise RuntimeError("MenuItem doesn't support adding " +\
                "arbitrary kind of widgets, " +\
                "just Menu widgets are allowed")
        super(MenuItem, self).set_submenu(menu)
        return menu

class SeparatorMenuItem(Gtk.SeparatorMenuItem, WidgetMixin):
    def add(self, menu):
        if not isinstance(menu, MenuItem):
            raise RuntimeError("MenuItem doesn't support adding " +\
                "arbitrary kind of widgets, " +\
                "just Menu widgets are allowed")
        super(MenuItem, self).set_submenu(menu)
        return menu

class MenuBar(Gtk.MenuBar, WidgetMixin):
    def add(self, menu_entry):
        if not isinstance(menu_entry, MenuItem):
            raise RuntimeError("MenuBar doesn't support adding " +\
                "arbitrary kind of widgets, " +\
                "just MenuItem widgets are allowed")
        self.append(menu_entry)       
        return menu_entry

class Label(Gtk.Label, WidgetMixin):
    def __new__(cls, *args, line_breaks=False, **kwargs):
        if not line_breaks:
            return super().__new__(cls, *args, **kwargs)
        else:
            class MultilineLabel(Gtk.TextView, WidgetMixin):
                def __init__(self, text, *args, **kwargs):
                    super().__init__()
                    self._buffer = Gtk.TextBuffer()
                    self.set_buffer(self._buffer)
                    self.set_wrap_mode(Gtk.WrapMode.WORD)

                    # get window foreground color:
                    w = Gtk.Window()
                    w.realize()
                    context = w.get_style_context()
                    bg_color = context.get_background_color(
                        Gtk.StateType.NORMAL)
                    w.destroy()
                    del(w)

                    # get the label foreground color:
                    l = Gtk.Window()
                    l.realize()
                    context = l.get_style_context()
                    fg_color = context.get_color(
                        Gtk.StateType.NORMAL)
                    l.destroy()
                    del(l)

                    self.override_background_color(Gtk.StateType.NORMAL,
                        bg_color)
                    self.override_color(Gtk.StateType.NORMAL, fg_color)
                    self.set_editable(False)
                    self.set_cursor_visible(False)
                    self._buffer.set_text(text)
                    return

                def set_alignment(self, *args, **kwargs):
                    """ This is supported by Gtk.Label, but not by our
                        multiline label -> we ignore it. """
                    pass  
            return MultilineLabel(*args, **kwargs)
 
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
        return tab_widget

class RadioButton(Gtk.RadioButton, WidgetMixin):
    def __new__(cls, text=None, group=None, **kwargs):
        if text == None:
            return super(Gtk.RadioButton, cls).__new__(cls, group,
                *args, **kwargs)
        button = Gtk.RadioButton.new_with_label_from_widget(\
            group, text)
        button.__class__ = type("RadioButton", (Gtk.RadioButton, WidgetMixin),
            {})
        return button

    def __init__(self, *args, **kwargs):
        super(RadioButton, self).__init__(*args, **kwargs)
        self.connect("clicked", lambda button: self.trigger("click"))
        self.connect("toggled", lambda button: self.trigger("click"))

class Button(Gtk.Button, WidgetMixin):
    def __init__(self, *args, **kwargs):
        super(Button, self).__init__(*args, **kwargs)
        self.connect("clicked", lambda button: self.trigger("click"))

class ComboBoxText(Gtk.ComboBoxText, WidgetMixin):
    pass

class TextEntry(Gtk.Entry, WidgetMixin):
    pass

class Dialog(Gtk.Dialog, WidgetMixin):
    def __init__(self, *args, **kwargs):
        super(Dialog, self).__init__(*args, **kwargs)
        #print("class of action area: " + str(self.action_area.__class__))
        #self.action_area.__class__ = type("ButtonBox",
        #    (self.action_area.__class__, AddInsteadOfPackMixin),
        #    {})
        #print("new class: " + str(self.action_area.__class__))
        #print(".add member: " + str(self.action_area.add))

    @staticmethod
    def show_error(text, title="Error", parent=None):
        print("TEXT: " + str(text))
        print("TITLE: " + str(title))
        dialog = Gtk.MessageDialog(parent, 0, Gtk.MessageType.ERROR,
            Gtk.ButtonsType.OK, title)
        dialog.format_secondary_text(text)
        dialog.run()
        dialog.destroy()

    @staticmethod
    def show_yesno(text, title="Error", parent=None):
        print("TEXT: " + str(text))
        print("TITLE: " + str(title))
        dialog = Gtk.MessageDialog(parent, 0, Gtk.MessageType.ERROR,
            buttons=(Gtk.STOCK_NO, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_YES, Gtk.ResponseType.OK))
        dialog.set_title(title)
        dialog.format_secondary_text(text)
        response = dialog.run()
        dialog.destroy()
        if response == Gtk.ResponseType.OK:
            return True
        return False

class List(WidgetMixin):
    def append(self, text_or_widget):
        pass

class AboutDialog(Gtk.AboutDialog, WidgetMixin):
    pass

