# Python imports
import os

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import Gio

# Application imports
from plugins.plugin_base import PluginBase
from .xdgtrash import XDGTrash




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
        trash_a = Gtk.MenuItem("Trash Actions")
        trash_menu = Gtk.Menu()

        self.restore = Gtk.ImageMenuItem("Restore From Trash")
        self.restore.set_image( Gtk.Image.new_from_icon_name("gtk-undelete", 3) )
        self.restore.connect("activate", self.restore_trash_files)

        self.empty = Gtk.ImageMenuItem("Empty Trash")
        self.empty.set_image( Gtk.Image.new_from_icon_name("gtk-delete", 3) )
        self.empty.connect("activate", self.empty_trash)

        trash = Gtk.ImageMenuItem("Trash")
        trash.set_image( Gtk.Image.new_from_icon_name("user-trash", 3) )
        trash.connect("activate", self.trash_files)
        trash.set_always_show_image(True)

        go_to = Gtk.ImageMenuItem("Go To Trash")
        go_to.set_image( Gtk.Image.new_from_icon_name("gtk-go-forward", 3) )
        go_to.connect("activate", self.go_to_trash)
        go_to.set_always_show_image(True)

        delete = Gtk.ImageMenuItem("Delete")
        delete.set_image( Gtk.Image(stock=Gtk.STOCK_DELETE) )
        delete.connect("activate", self.delete_files)
        delete.set_always_show_image(True)

        trash_a.set_submenu(trash_menu)
        trash_a.show_all()
        self._appen_menu_items(trash_menu, [self.restore, self.empty, trash, go_to, delete])

        return trash_a


    def _appen_menu_items(self, menu, items):
        for item in items:
            menu.append(item)


    def _show_trash_buttons(self):
        self.restore.show()
        self.empty.show()

    def _hide_trash_buttons(self):
        self.restore.hide()
        self.empty.hide()

    def delete_files(self, widget = None, eve = None):
        self._event_system.emit("get_current_state")
        state    = self._fm_state
        uris     = state.uris
        response = None

        state.message_dialog.format_secondary_text(f"Do you really want to delete the {len(uris)} file(s)?")
        for uri in uris:
            file = Gio.File.new_for_path(uri)

            if not response:
                response = state.message_dialog.run()
                state.message_dialog.hide()
            if response == Gtk.ResponseType.YES:
                type = file.query_file_type(flags=Gio.FileQueryInfoFlags.NONE)

                if type == Gio.FileType.DIRECTORY:
                    state.tab.delete_file( file.get_path() )
                else:
                    file.delete(cancellable=None)
            else:
                break

    def trash_files(self, widget = None, eve = None, verbocity = False):
        self._event_system.emit("get_current_state")
        state = self._fm_state
        for uri in state.uris:
            self.trashman.trash(uri, verbocity)

    def restore_trash_files(self, widget = None, eve = None, verbocity = False):
        self._event_system.emit("get_current_state")
        state = self._fm_state
        for uri in state.uris:
            self.trashman.restore(filename=uri.split("/")[-1], verbose = verbocity)

    def empty_trash(self, widget = None, eve = None, verbocity = False):
        self.trashman.empty(verbose = verbocity)

    def go_to_trash(self, widget = None, eve = None, verbocity = False):
        self._event_system.emit("go_to_path", self.trash_files_path)
