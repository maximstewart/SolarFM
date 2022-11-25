# Python imports
import os, threading, subprocess, time, inspect

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Application imports
from plugins.plugin_base import PluginBase


# NOTE: Threads WILL NOT die with parent's destruction.
def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs, daemon=False).start()
    return wrapper

# NOTE: Threads WILL die with parent's destruction.
def daemon_threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs, daemon=True).start()
    return wrapper




class Plugin(PluginBase):
    def __init__(self):
        super().__init__()

        self.name        = "Disk Usage"  # NOTE: Need to remove after establishing private bidirectional 1-1 message bus
                                         #       where self.name should not be needed for message comms

        self.path        = os.path.dirname(os.path.realpath(__file__))
        self._GLADE_FILE = f"{self.path}/du_usage.glade"
        self._du_dialog  = None
        self._du_store   = None


    def run(self):
        self._builder    = Gtk.Builder()
        self._builder.add_from_file(self._GLADE_FILE)

        classes  = [self]
        handlers = {}
        for c in classes:
            methods = None
            try:
                methods = inspect.getmembers(c, predicate=inspect.ismethod)
                handlers.update(methods)
            except Exception as e:
                print(repr(e))

        self._builder.connect_signals(handlers)

        self._du_dialog = self._builder.get_object("du_dialog")
        self._du_store  = self._builder.get_object("du_store")
        self._current_dir_lbl  = self._builder.get_object("current_dir_lbl")

        self._event_system.subscribe("show_du_menu", self._show_du_menu)

    def generate_reference_ui_element(self):
        item = Gtk.ImageMenuItem(self.name)
        item.set_image( Gtk.Image(stock=Gtk.STOCK_HARDDISK) )
        item.connect("activate", self._show_du_menu)
        item.set_always_show_image(True)
        return item

    def _get_state(self, widget=None, eve=None):
        self._event_system.emit("get_current_state")

    def _set_current_dir_lbl(self, widget=None, eve=None):
        self._current_dir_lbl.set_label(f"Current Directory:\n{self._fm_state.tab.get_current_directory()}")

    def _show_du_menu(self, widget=None, eve=None):
        self._fm_state = None
        self._get_state()
        self._set_current_dir_lbl()
        self.load_du_data()
        self._du_dialog.run()

    def load_du_data(self):
        self._du_store.clear()

        path     = self._fm_state.tab.get_current_directory()
        # NOTE: -h = human readable, -d = depth asigned to 1
        command  = ["du", "-h", "-d", "1", path]
        proc     = subprocess.Popen(command, stdout=subprocess.PIPE)
        raw_data = proc.communicate()[0]
        data     = raw_data.decode("utf-8").strip()  # NOTE: Will return data AFTER completion (if any)
        parts    = data.split("\n")

        # NOTE: Last entry is curret dir. Move to top of list and pop off...
        size, file = parts[-1].split("\t")
        self._du_store.append([size, file.split("/")[-1]])
        parts.pop()

        for part in parts:
            size, file = part.split("\t")
            self._du_store.append([size, file.split("/")[-1]])

    def _hide_du_menu(self, widget=None, eve=None):
        self._du_dialog.hide()
