# Python imports
import os, threading, subprocess, inspect, time, json, base64, shlex, select, signal

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

# Application imports
from plugins.plugin_base import PluginBase
from .ipc_server import IPCServer



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




class FilePreviewWidget(Gtk.LinkButton):
    def __init__(self, path, file):
        super(FilePreviewWidget, self).__init__()
        self.set_label(file)
        self.set_uri(f"file://{path}")
        self.show_all()


class GrepPreviewWidget(Gtk.Box):
    def __init__(self, _path, sub_keys, data):
        super(GrepPreviewWidget, self).__init__()
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.line_color = "#e0cc64"

        path   = base64.urlsafe_b64decode(_path.encode('utf-8')).decode('utf-8')
        _label = '/'.join( path.split("/")[-3:] )
        title  = Gtk.LinkButton.new_with_label(uri=f"file://{path}", label=_label)

        self.add(title)
        for key in sub_keys:
            line_num     = key
            text = base64.urlsafe_b64decode(data[key].encode('utf-8')).decode('utf-8')


            box          = Gtk.Box()
            number_label = Gtk.Label()
            text_view    = Gtk.Label(label=text[:-1])
            label_text   = f"<span foreground='{self.line_color}'>{line_num}</span>"

            number_label.set_markup(label_text)
            number_label.set_margin_left(15)
            number_label.set_margin_right(5)
            number_label.set_margin_top(5)
            number_label.set_margin_bottom(5)
            text_view.set_margin_top(5)
            text_view.set_margin_bottom(5)
            text_view.set_line_wrap(True)

            box.add(number_label)
            box.add(text_view)
            self.add(box)

        self.show_all()


pause_fifo_update = False

class Plugin(IPCServer, PluginBase):
    def __init__(self):
        super().__init__()

        self.path              = os.path.dirname(os.path.realpath(__file__))
        self.name              = "Search"  # NOTE: Need to remove after establishing private bidirectional 1-1 message bus
                                           #       where self.name should not be needed for message comms
        self._GLADE_FILE       = f"{self.path}/search_dialog.glade"

        self._search_dialog    = None
        self._active_path      = None
        self._file_list        = None
        self._grep_list        = None
        self._grep_proc        = None
        self._list_proc        = None


    def get_ui_element(self):
        button = Gtk.Button(label=self.name)
        button.connect("button-release-event", self._show_grep_list_page)
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

        self._search_dialog = self._builder.get_object("search_dialog")
        self._grep_list     = self._builder.get_object("grep_list")
        self._file_list     = self._builder.get_object("file_list")
        self.fsearch        = self._builder.get_object("fsearch")

        self._event_system.subscribe("update-file-ui", self._load_file_ui)
        self._event_system.subscribe("update-grep-ui", self._load_grep_ui)

        self.create_ipc_listener()


    def _show_grep_list_page(self, widget=None, eve=None):
        self._event_system.emit("get_current_state")

        state               = self._fm_state
        self._event_message = None

        self._active_path   = state.tab.get_current_directory()
        response            = self._search_dialog.run()
        self._search_dialog.hide()


    def _run_find_file_query(self, widget=None, eve=None):
        self._stop_find_file_query()

        query = widget.get_text()
        if not query in ("", None):
            target_dir = shlex.quote( self._fm_state.tab.get_current_directory() )
            command = ["python", f"{self.path}/search.py", "-t", "file_search", "-d", f"{target_dir}", "-q", f"{query}"]
            process = subprocess.Popen(command, cwd=self.path, stdin=None, stdout=None, stderr=None)

    def _stop_find_file_query(self, widget=None, eve=None):
        pause_fifo_update = True

        if self._list_proc:
            if self._list_proc.poll():
                self._list_proc.send_signal(signal.SIGKILL)
                while self._list_proc.poll():
                    pass

                self._list_proc = None
            else:
                self._list_proc = None

        self.clear_children(self._file_list)
        pause_fifo_update = False


    def _run_grep_query(self, widget=None, eve=None):
        self._stop_grep_query()

        query = widget.get_text()
        if not query in ("", None):
            target_dir = shlex.quote( self._fm_state.tab.get_current_directory() )
            command = ["python", f"{self.path}/search.py", "-t", "grep_search", "-d", f"{target_dir}", "-q", f"{query}"]
            process = subprocess.Popen(command, cwd=self.path, stdin=None, stdout=None, stderr=None)

    def _stop_grep_query(self, widget=None, eve=None):
        pause_fifo_update = True

        if self._grep_proc:
            if self._grep_proc.poll():
                self._grep_proc.send_signal(signal.SIGKILL)
                while self._grep_proc.poll():
                    pass

                self._grep_proc = None
            else:
                self._grep_proc = None

        self.clear_children(self._grep_list)
        pause_fifo_update = False


    def _load_file_ui(self, data):
        if not data in ("", None) and not pause_fifo_update:
            jdata  = json.loads( data )
            target = jdata[0]
            file   = jdata[1]

            widget = FilePreviewWidget(target, file)
            self._file_list.add(widget)

    def _load_grep_ui(self, data):
        if not data in ("", None) and not pause_fifo_update:
            jdata = json.loads( data )
            jkeys = jdata.keys()
            for key in jkeys:
                sub_keys    = jdata[key].keys()
                grep_result = jdata[key]

                widget = GrepPreviewWidget(key, sub_keys, grep_result)
                self._grep_list.add(widget)
