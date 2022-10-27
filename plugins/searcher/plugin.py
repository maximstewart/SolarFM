# Python imports
import os, threading, inspect, time

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

# Application imports
from plugins.plugin_base import PluginBase
from .mixins.file_search_mixin import FileSearchMixin
from .mixins.grep_search_mixin import GrepSearchMixin
from .utils.ipc_server import IPCServer



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




class Plugin(IPCServer, FileSearchMixin, GrepSearchMixin, PluginBase):
    def __init__(self):
        super().__init__()

        self.path              = os.path.dirname(os.path.realpath(__file__))
        self.name              = "Search"  # NOTE: Need to remove after establishing private bidirectional 1-1 message bus
                                           #       where self.name should not be needed for message comms
        self._GLADE_FILE       = f"{self.path}/search_dialog.glade"

        self._search_dialog    = None
        self._active_path      = None
        self.file_list_parent  = None
        self.grep_list_parent  = None
        self._file_list        = None
        self._grep_list        = None
        self._grep_proc        = None
        self._list_proc        = None
        self.pause_fifo_update = False
        self.update_list_ui_buffer = ()
        self.grep_query        = ""
        self.search_query      = ""


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

        self._search_dialog = self._builder.get_object("search_dialog")
        self.fsearch        = self._builder.get_object("fsearch")

        self.grep_list_parent = self._builder.get_object("grep_list_parent")
        self.file_list_parent = self._builder.get_object("file_list_parent")

        self._event_system.subscribe("update-file-ui", self._load_file_ui)
        self._event_system.subscribe("update-grep-ui", self._load_grep_ui)
        self._event_system.subscribe("show_search_page", self._show_page)


        self.create_ipc_listener()

    def generate_reference_ui_element(self):
        item = Gtk.ImageMenuItem(self.name)
        item.set_image( Gtk.Image(stock=Gtk.STOCK_FIND) )
        item.connect("activate", self._show_page)
        item.set_always_show_image(True)
        return item


    def _show_page(self, widget=None, eve=None):
        self._event_system.emit("get_current_state")

        state               = self._fm_state
        self._event_message = None

        self._active_path   = state.tab.get_current_directory()
        response            = self._search_dialog.run()
        self._search_dialog.hide()

    # TODO: Merge the below methods into some unified logic
    def reset_grep_box(self) -> None:
        try:
            child = self.grep_list_parent.get_children()[0]
            self._grep_list = None
            self.grep_list_parent.remove(child)
        except Exception:
            ...

        self._grep_list = Gtk.Box()
        self._grep_list.set_orientation(Gtk.Orientation.VERTICAL)
        self.grep_list_parent.add(self._grep_list)
        self.grep_list_parent.show_all()

        time.sleep(0.05)
        Gtk.main_iteration()

    def reset_file_list_box(self) -> None:
        try:
            child = self.file_list_parent.get_children()[0]
            self._file_list = None
            self.file_list_parent.remove(child)
        except Exception:
            ...

        self._file_list = Gtk.Box()
        self._file_list.set_orientation(Gtk.Orientation.VERTICAL)
        self.file_list_parent.add(self._file_list)
        self.file_list_parent.show_all()

        time.sleep(0.05)
        Gtk.main_iteration()
