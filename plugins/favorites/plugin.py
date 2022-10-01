# Python imports
import os, threading, subprocess, time, inspect, json

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

        self.name               = "Favorites"  # NOTE: Need to remove after establishing private bidirectional 1-1 message bus
                                                      #       where self.name should not be needed for message comms
        self.path               = os.path.dirname(os.path.realpath(__file__))
        self._GLADE_FILE        = f"{self.path}/favorites.glade"
        self._FAVORITES_FILE    = f"{self.path}/favorites.json"

        self._favorites_dialog  = None
        self._favorites_store   = None
        self._favorites         = None
        self._selected          = None


    def get_ui_element(self):
        button = Gtk.Button(label=self.name)
        button.connect("button-release-event", self._show_favorites_menu)
        return button

    def run(self):
        self._builder          = Gtk.Builder()
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

        self._favorites_dialog = self._builder.get_object("favorites_dialog")
        self._favorites_store  = self._builder.get_object("favorites_store")
        self._current_dir_lbl  = self._builder.get_object("current_dir_lbl")

        if os.path.exists(self._FAVORITES_FILE):
            with open(self._FAVORITES_FILE) as f:
                self._favorites = json.load(f)
                for favorite in self._favorites:
                    self._favorites_store.append([favorite])
        else:
            with open(self._FAVORITES_FILE, 'a') as f:
                f.write('[]')


    @threaded
    def _get_state(self, widget=None, eve=None):
        self._event_system.emit("get_current_state


    @threaded
    def _set_current_dir_lbl(self, widget=None, eve=None):
        self._current_dir_lbl.set_label(f"Current Directory:\n{self._fm_state.tab.get_current_directory()}")

    def _add_to_favorite(self, state):
        current_directory = self._fm_state.tab.get_current_directory()
        self._favorites_store.append([current_directory])
        self._favorites.append(current_directory)
        self._save_favorites()

    def _remove_from_favorite(self, state):
        path = self._favorites_store.get_value(self._selected, 0)
        self._favorites_store.remove(self._selected)
        self._favorites.remove(path)
        self._save_favorites()

    def _save_favorites(self):
        with open(self._FAVORITES_FILE, 'w') as outfile:
            json.dump(self._favorites, outfile, separators=(',', ':'), indent=4)

    def _set_selected_path(self, widget=None, eve=None):
        path = self._favorites_store.get_value(self._selected, 0)
        self._ui_objects[0].set_text(path)
        self._set_current_dir_lbl()

    def _show_favorites_menu(self, widget=None, eve=None):
        self._fm_state = None
        self._get_state()
        self._set_current_dir_lbl()
        self._favorites_dialog.run()

    def _hide_favorites_menu(self, widget=None, eve=None):
        self._favorites_dialog.hide()

    def _set_selected(self, user_data):
        selected = user_data.get_selected()[1]
        if selected:
            self._selected = selected
