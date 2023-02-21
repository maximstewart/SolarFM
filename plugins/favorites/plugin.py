# Python imports
import os
import json

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Application imports
from plugins.plugin_base import PluginBase




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


    def run(self):
        self._builder = Gtk.Builder()
        self._builder.add_from_file(self._GLADE_FILE)
        self._connect_builder_signals(self, self._builder)

        self._favorites_dialog = self._builder.get_object("favorites_dialog")
        self._favorites_store  = self._builder.get_object("favorites_store")
        self._current_dir_lbl  = self._builder.get_object("current_dir_lbl")

        if os.path.exists(self._FAVORITES_FILE):
            with open(self._FAVORITES_FILE) as f:
                self._favorites = json.load(f)
                for favorite in self._favorites:
                    display, path = favorite
                    self._favorites_store.append([display, path])
        else:
            with open(self._FAVORITES_FILE, 'a') as f:
                f.write('[]')

        self._event_system.subscribe("show_favorites_menu", self._show_favorites_menu)


    def generate_reference_ui_element(self):
        button = Gtk.Button(label=self.name)
        button.connect("button-release-event", self._show_favorites_menu)
        return button

    def _get_state(self, widget=None, eve=None):
        self._event_system.emit("get_current_state")

    def _set_current_dir_lbl(self, widget=None, eve=None):
        self._current_dir_lbl.set_label(f"Current Directory:\n{self._fm_state.tab.get_current_directory()}")

    def _add_to_favorite(self, state):
        path    = self._fm_state.tab.get_current_directory()
        parts   = path.split("/")
        display = '/'.join(parts[-3:]) if len(parts) > 3 else path

        self._favorites_store.append([display, path])
        self._favorites.append([display, path])
        self._save_favorites()

    def _remove_from_favorite(self, state):
        path = self._favorites_store.get_value(self._selected, 1)
        self._favorites_store.remove(self._selected)

        for i, f in enumerate(self._favorites):
            if f[1] == path:
                self._favorites.remove( self._favorites[i] )

        self._save_favorites()

    def _save_favorites(self):
        with open(self._FAVORITES_FILE, 'w') as outfile:
            json.dump(self._favorites, outfile, separators=(',', ':'), indent=4)

    def _set_selected_path(self, widget=None, eve=None):
        path = self._favorites_store.get_value(self._selected, 1)
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
        if selected and not self._selected == selected:
            self._selected = selected
