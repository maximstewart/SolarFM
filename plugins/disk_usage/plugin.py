# Python imports
import os
import subprocess
import time

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Application imports
from plugins.plugin_base import PluginBase




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
        self._builder = Gtk.Builder()
        self._builder.add_from_file(self._GLADE_FILE)
        self._connect_builder_signals(self, self._builder)

        self._du_dialog    = self._builder.get_object("du_dialog")
        self._du_tree_view = self._builder.get_object("du_tree_view")
        self._du_store     = self._builder.get_object("du_store")
        self._current_dir_lbl  = self._builder.get_object("current_dir_lbl")

        self._current_dir_lbl.set_line_wrap(False)
        self._current_dir_lbl.set_ellipsize(1)  # NONE = 0¶, START = 1¶, MIDDLE = 2¶, END = 3¶

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
        path = self._fm_state.tab.get_current_directory()
        self._current_dir_lbl.set_label(path)
        self._current_dir_lbl.set_tooltip_text(path)

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
        proc     = subprocess.Popen(command, stdout=subprocess.PIPE, encoding="utf-8")
        raw_data = proc.communicate()[0]
        # NOTE: Will return data AFTER completion (if any)
        data     = raw_data.strip()
        parts    = data.split("\n")

        # NOTE: Last entry is curret dir. Move to top of list and pop off...
        size, file = parts[-1].split("\t")
        self._du_tree_view.set_title(f"Disk Usage: {file.split('/')[-1]} ( {size} )")
        parts.pop()

        for part in parts:
            size, file = part.split("\t")
            self._du_store.append([size, file.split("/")[-1]])

    def _hide_du_menu(self, widget=None, eve=None):
        self._du_dialog.hide()
