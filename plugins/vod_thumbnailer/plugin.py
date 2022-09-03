# Python imports
import os, threading, subprocess, time, inspect, hashlib
from datetime import datetime

# Gtk imports
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import Gtk, GLib, Gio, GdkPixbuf

# Application imports


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




class Plugin:
    def __init__(self):
        self.path                   = os.path.dirname(os.path.realpath(__file__))
        self.name                   = "VOD Thumbnailer"  # NOTE: Need to remove after establishing private bidirectional 1-1 message bus
                                                         #       where self.name should not be needed for message comms
        self._GLADE_FILE            = f"{self.path}/re_thumbnailer.glade"
        self._builder               = None
        self._thumbnailer_dialog    = None
        self._thumbnail_preview_img = None
        self._scrub_step            = None
        self._file_name             = None
        self._file_location         = None
        self._file_hash             = None
        self._state                 = None

        self._event_system          = None
        self._event_sleep_time      = .5
        self._event_message         = None



    def get_ui_element(self):
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

        self._thumbnailer_dialog    = self._builder.get_object("thumbnailer_dialog")
        self._scrub_step            = self._builder.get_object("scrub_step")
        self._file_name             = self._builder.get_object("file_name")
        self._file_location         = self._builder.get_object("file_location")
        self._thumbnail_preview_img = self._builder.get_object("thumbnail_preview_img")
        self._file_hash             = self._builder.get_object("file_hash")

        button = Gtk.Button(label=self.name)
        button.connect("button-release-event", self._show_thumbnailer_page)
        return button

    def set_fm_event_system(self, fm_event_system):
        self._event_system = fm_event_system

    def run(self):
        self._module_event_observer()




    @threaded
    def _show_thumbnailer_page(self, widget=None, eve=None):
        self._event_system.push_gui_event([self.name, "get_current_state", ()])
        self.wait_for_fm_message()

        state               = self._event_message
        self._event_message = None

        GLib.idle_add(self._process_changes, (state))

    def _process_changes(self, state):
        self._state = None

        if len(state.selected_files) == 1:
            if state.selected_files[0].lower().endswith(state.tab.fvideos):
                self._state = state
                self._set_ui_data()
                response   = self._thumbnailer_dialog.run()
                if response in [Gtk.ResponseType.CLOSE, Gtk.ResponseType.DELETE_EVENT]:
                    self._thumbnailer_dialog.hide()


    def _regenerate_thumbnail(self, widget=None, eve=None):
        scrub_percent = int(self._scrub_step.get_value())
        file          = self._file_name.get_text()
        dir           = self._file_location.get_text()
        file_hash     = self._file_hash.get_text()
        hash_img_pth  = f"{self._state.tab.ABS_THUMBS_PTH}/{file_hash}.jpg"

        try:
            os.remove(hash_img_pth) if os.path.isfile(hash_img_pth) else ...

            self._state.tab.create_thumbnail(dir, file, f"{scrub_percent}%")
            preview_pixbuf = GdkPixbuf.Pixbuf.new_from_file(hash_img_pth)
            self._thumbnail_preview_img.set_from_pixbuf(preview_pixbuf)

            img_pixbuf = self._state.tab.create_scaled_image(hash_img_pth)
            tree_pth   = self._state.icon_grid.get_selected_items()[0]
            itr        = self._state.store.get_iter(tree_pth)
            pixbuff    = self._state.store.get(itr, 0)[0]
            self._state.store.set(itr, 0, img_pixbuf)
        except Exception as e:
            print(repr(e))
            print("Couldn't regenerate thumbnail!")


    def _set_ui_data(self):
        uri            = self._state.selected_files[0]
        path           = self._state.tab.get_current_directory()
        parts          = uri.split("/")

        file_hash      = hashlib.sha256(str.encode(uri)).hexdigest()
        hash_img_pth   = f"{self._state.tab.ABS_THUMBS_PTH}/{file_hash}.jpg"
        preview_pixbuf = GdkPixbuf.Pixbuf.new_from_file(hash_img_pth)

        self._thumbnail_preview_img.set_from_pixbuf(preview_pixbuf)
        self._file_name.set_text(parts[ len(parts) - 1 ])
        self._file_location.set_text(path)
        self._file_hash.set_text(file_hash)



    def wait_for_fm_message(self):
        while not self._event_message:
            pass

    @daemon_threaded
    def _module_event_observer(self):
        while True:
            time.sleep(self._event_sleep_time)
            event = self._event_system.read_module_event()
            if event:
                try:
                    if event[0] == self.name:
                        target_id, method_target, data = self._event_system.consume_module_event()

                        if not method_target:
                            self._event_message = data
                        else:
                            method = getattr(self.__class__, f"{method_target}")
                            if data:
                                data = method(*(self, *data))
                            else:
                                method(*(self,))
                except Exception as e:
                    print(repr(e))
