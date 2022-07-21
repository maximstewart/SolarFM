# Python imports
import os, multiprocessing, threading, subprocess, inspect, time, json
from multiprocessing import Manager, Process

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, GObject

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




class Manifest:
    path: str     = os.path.dirname(os.path.realpath(__file__))
    name: str     = "Search"
    author: str   = "ITDominator"
    version: str  = "0.0.1"
    support: str  = ""
    requests: {}  = {
        'ui_target': "context_menu",
        'pass_fm_events': "true",
        'bind_keys': [f"{name}||_show_grep_list_page:<Control>f"]
    }




class FilePreviewWidget(Gtk.LinkButton):
    def __init__(self, path, file):
        super(FilePreviewWidget, self).__init__()
        self.set_label(file)
        self.set_uri(f"file://{path}")
        self.show_all()


class GrepPreviewWidget(Gtk.Box):
    def __init__(self, path, sub_keys, data):
        super(GrepPreviewWidget, self).__init__()
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.line_color = "#e0cc64"


        _label = '/'.join( path.split("/")[-3:] )
        title  = Gtk.LinkButton.new_with_label(uri=f"file://{path}", label=_label)

        self.add(title)
        for key in sub_keys:
            line_num     = key
            text         = data[key]
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



manager  = Manager()
grep_result_set  = manager.dict()
file_result_set  = manager.list()


class Plugin(Manifest):
    def __init__(self):
        self._GLADE_FILE       = f"{self.path}/search_dialog.glade"
        self._builder          = None
        self._search_dialog    = None

        self._event_system     = None
        self._event_sleep_time = .5
        self._event_message    = None

        self._active_path      = None
        self._file_list        = None
        self._grep_list        = None
        self._grep_proc        = None
        self._list_proc        = None


    def get_ui_element(self):
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

        GObject.signal_new("update-file-ui-signal", self._search_dialog, GObject.SIGNAL_RUN_LAST, GObject.TYPE_PYOBJECT, (GObject.TYPE_PYOBJECT,))
        self._search_dialog.connect("update-file-ui-signal", self._load_file_ui)
        GObject.signal_new("update-grep-ui-signal", self._search_dialog, GObject.SIGNAL_RUN_LAST, GObject.TYPE_PYOBJECT, (GObject.TYPE_PYOBJECT,))
        self._search_dialog.connect("update-grep-ui-signal", self._load_grep_ui)

        button = Gtk.Button(label=self.name)
        button.connect("button-release-event", self._show_grep_list_page)
        return button

    def set_fm_event_system(self, fm_event_system):
        self._event_system = fm_event_system

    def run(self):
        self._module_event_observer()


    @daemon_threaded
    def _show_grep_list_page(self, widget=None, eve=None):
        self._event_system.push_gui_event([self.name, "get_current_state", ()])
        self.wait_for_fm_message()

        state               = self._event_message
        self._event_message = None

        GLib.idle_add(self._process_queries, (state))

    def _process_queries(self, state):
        self._active_path   = state.tab.get_current_directory()
        response            = self._search_dialog.run()
        self._search_dialog.hide()


    def _run_find_file_query(self, widget=None, eve=None):
        if self._list_proc:
            self._list_proc.terminate()
            self._list_proc = None
            time.sleep(.2)

        del file_result_set[:]
        self.clear_children(self._file_list)

        query = widget.get_text()
        if query:
            self._list_proc = multiprocessing.Process(self._do_list_search(self._active_path, query))
            self._list_proc.start()

    def _do_list_search(self, path, query):
        self._file_traverse_path(path, query)
        for target, file in file_result_set:
            widget = FilePreviewWidget(target, file)
            self._search_dialog.emit("update-file-ui-signal", (widget))

    def _load_file_ui(self, parent=None, widget=None):
        self._file_list.add(widget)

    def _file_traverse_path(self, path, query):
        try:
            for file in os.listdir(path):
                target = os.path.join(path, file)
                if os.path.isdir(target):
                    self._file_traverse_path(target, query)
                else:
                    if query.lower() in file.lower():
                        file_result_set.append([target, file])
        except Exception as e:
            if debug:
                print("Couldn't traverse to path. Might be permissions related...")


    def _run_grep_query(self, widget=None, eve=None):
        if self._grep_proc:
            self._grep_proc.terminate()
            self._grep_proc = None
            time.sleep(.2)

        grep_result_set.clear()
        self.clear_children(self._grep_list)

        query = widget.get_text()
        if query:
            self._grep_proc = multiprocessing.Process(self._do_grep_search(self._active_path, query))
            self._grep_proc.start()

    def _do_grep_search(self, path, query):
        self._grep_traverse_path(path, query)

        keys = grep_result_set.keys()
        for key in keys:
            sub_keys = grep_result_set[key].keys()
            widget   = GrepPreviewWidget(key, sub_keys, grep_result_set[key])
            self._search_dialog.emit("update-grep-ui-signal", (widget))

    def _load_grep_ui(self, parent=None, widget=None):
        self._grep_list.add(widget)

    def _grep_traverse_path(self, path, query):
        try:
            for file in os.listdir(path):
                target = os.path.join(path, file)
                if os.path.isdir(target):
                    self._grep_traverse_path(target, query)
                else:
                    self._search_for_string(target, query)
        except Exception as e:
            if debug:
                print("Couldn't traverse to path. Might be permissions related...")

    def _search_for_string(self, file, query):
        try:
            with open(file, 'r') as fp:
                for i, line in enumerate(fp):
                    if query in line:
                        if f"{file}" in grep_result_set.keys():
                            grep_result_set[f"{file}"][f"{i+1}"] = line
                        else:
                            grep_result_set[f"{file}"] = {}
                            grep_result_set[f"{file}"] = {f"{i+1}": line}
        except Exception as e:
            if debug:
                print("Couldn't read file. Might be binary or other cause...")




    def clear_children(self, widget: type) -> None:
        ''' Clear children of a gtk widget. '''
        for child in widget.get_children():
            widget.remove(child)

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
