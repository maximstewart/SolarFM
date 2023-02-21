# Python imports
import os
import threading
import subprocess
import time
import hashlib
from datetime import datetime

# Gtk imports
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import Gio
from gi.repository import GdkPixbuf

# Application imports
from plugins.plugin_base import PluginBase


# NOTE: Threads WILL NOT die with parent's destruction.
def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs, daemon=False).start()
    return wrapper




class Plugin(PluginBase):
    def __init__(self):
        super().__init__()

        self.path                   = os.path.dirname(os.path.realpath(__file__))
        self._GLADE_FILE            = f"{self.path}/re_thumbnailer.glade"
        self.name                   = "VOD Thumbnailer"  # NOTE: Need to remove after establishing private bidirectional 1-1 message bus
                                                         #       where self.name should not be needed for message comms

        self._thumbnailer_dialog    = None
        self._thumbnail_preview_img = None
        self._scrub_step            = None
        self._file_name             = None
        self._file_location         = None
        self._file_hash             = None


    def run(self):
        self._builder = Gtk.Builder()
        self._builder.add_from_file(self._GLADE_FILE)
        self._connect_builder_signals(self, self._builder)

        self._thumbnailer_dialog    = self._builder.get_object("thumbnailer_dialog")
        self._scrub_step            = self._builder.get_object("scrub_step")
        self._file_name             = self._builder.get_object("file_name")
        self._file_location         = self._builder.get_object("file_location")
        self._thumbnail_preview_img = self._builder.get_object("thumbnail_preview_img")
        self._file_hash             = self._builder.get_object("file_hash")

    def generate_reference_ui_element(self):
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(f"{self.path}/../../icons/video.png", 16, 16, True)
        icon   = Gtk.Image.new_from_pixbuf(pixbuf)
        item   = Gtk.ImageMenuItem(self.name)

        item.set_image( icon )
        item.connect("activate", self._show_thumbnailer_page)
        item.set_always_show_image(True)
        return item


    @threaded
    def _show_thumbnailer_page(self, widget=None, eve=None):
        self._event_system.emit("get_current_state")

        state               = self._fm_state
        self._event_message = None

        GLib.idle_add(self._process_changes, (state))

    def _process_changes(self, state):
        self._fm_state = None

        if len(state.uris) == 1:
            if state.uris[0].lower().endswith(state.tab.fvideos):
                self._fm_state = state
                self._set_ui_data()
                response   = self._thumbnailer_dialog.run()
                if response in [Gtk.ResponseType.CLOSE, Gtk.ResponseType.DELETE_EVENT]:
                    self._thumbnailer_dialog.hide()


    def _regenerate_thumbnail(self, widget=None, eve=None):
        scrub_percent = int(self._scrub_step.get_value())
        file          = self._file_name.get_text()
        dir           = self._file_location.get_text()
        file_hash     = self._file_hash.get_text()
        hash_img_pth  = f"{self._fm_state.tab.ABS_THUMBS_PTH}/{file_hash}.jpg"

        try:
            self._fm_state.tab.create_video_thumbnail(f"{dir}/{file}", f"{scrub_percent}%", True)
            preview_pixbuf = GdkPixbuf.Pixbuf.new_from_file(hash_img_pth)
            self._thumbnail_preview_img.set_from_pixbuf(preview_pixbuf)

            img_pixbuf = self._fm_state.tab.create_scaled_image(hash_img_pth)
            tree_pth   = self._fm_state.icon_grid.get_selected_items()[0]
            itr        = self._fm_state.store.get_iter(tree_pth)
            pixbuff    = self._fm_state.store.get(itr, 0)[0]
            self._fm_state.store.set(itr, 0, img_pixbuf)
        except Exception as e:
            print(repr(e))
            print("Couldn't regenerate thumbnail!")


    def _set_ui_data(self):
        uri            = self._fm_state.uris[0]
        path           = self._fm_state.tab.get_current_directory()
        parts          = uri.split("/")
        file_hash      = self._fm_state.tab.fast_hash(uri)
        hash_img_pth   = f"{self._fm_state.tab.ABS_THUMBS_PTH}/{file_hash}.jpg"
        preview_pixbuf = GdkPixbuf.Pixbuf.new_from_file(hash_img_pth)

        self._thumbnail_preview_img.set_from_pixbuf(preview_pixbuf)
        self._file_name.set_text(parts[ len(parts) - 1 ])
        self._file_location.set_text(path)
        self._file_hash.set_text(file_hash)
