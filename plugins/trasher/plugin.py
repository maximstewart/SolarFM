# Python imports
import os, threading, subprocess, inspect

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gio

# Application imports
from plugins.plugin_base import PluginBase
from .xdgtrash import XDGTrash


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
        self.path               = os.path.dirname(os.path.realpath(__file__))
        self._GLADE_FILE        = f"{self.path}/trasher.glade"
        self.name               = "Trasher"  # NOTE: Need to remove after establishing private bidirectional 1-1 message bus
                                             #       where self.name should not be needed for message comms
        self.trashman           = XDGTrash()
        self.trash_files_path   = f"{GLib.get_user_data_dir()}/Trash/files"
        self.trash_info_path    = f"{GLib.get_user_data_dir()}/Trash/info"

        self.trashman.regenerate()


    def run(self):
        self._event_system.subscribe("show_trash_buttons", self._show_trash_buttons)
        self._event_system.subscribe("hide_trash_buttons", self._hide_trash_buttons)
        self._event_system.subscribe("delete_files", self.delete_files)
        self._event_system.subscribe("trash_files", self.trash_files)

    def generate_reference_ui_element(self):
        self._builder           = Gtk.Builder()
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

        trasher = self._builder.get_object("trasher")
        trasher.show_all()

        return trasher


    def _show_trash_buttons(self):
        self._builder.get_object("restore_from_trash").show()
        self._builder.get_object("empty_trash").show()

    def _hide_trash_buttons(self):
        self._builder.get_object("restore_from_trash").hide()
        self._builder.get_object("empty_trash").hide()

    def delete_files(self, widget = None, eve = None):
        self._event_system.emit("do_hide_context_menu")
        self._event_system.emit("get_current_state")
        state    = self._fm_state
        uris     = state.selected_files
        response = None

        state.warning_alert.format_secondary_text(f"Do you really want to delete the {len(uris)} file(s)?")
        for uri in uris:
            file = Gio.File.new_for_path(uri)

            if not response:
                response = state.warning_alert.run()
                state.warning_alert.hide()
            if response == Gtk.ResponseType.YES:
                type = file.query_file_type(flags=Gio.FileQueryInfoFlags.NONE)

                if type == Gio.FileType.DIRECTORY:
                    state.tab.delete_file( file.get_path() )
                else:
                    file.delete(cancellable=None)
            else:
                break

    def trash_files(self, widget = None, eve = None, verbocity = False):
        self._event_system.emit("do_hide_context_menu")
        self._event_system.emit("get_current_state")
        state = self._fm_state
        for uri in state.selected_files:
            self.trashman.trash(uri, verbocity)

    def restore_trash_files(self, widget = None, eve = None, verbocity = False):
        self._event_system.emit("do_hide_context_menu")
        self._event_system.emit("get_current_state")
        state = self._fm_state
        for uri in state.selected_files:
            self.trashman.restore(filename=uri.split("/")[-1], verbose = verbocity)

    def empty_trash(self, widget = None, eve = None, verbocity = False):
        self._event_system.emit("do_hide_context_menu")
        self.trashman.empty(verbose = verbocity)

    def go_to_trash(self, widget = None, eve = None, verbocity = False):
        self._event_system.emit("do_hide_context_menu")
        self._event_system.emit("go_to_path", self.trash_files_path)
