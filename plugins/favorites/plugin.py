# Python imports
import os, threading, subprocess, time, inspect, json

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

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
        self.name               = "Favorites"  # NOTE: Need to remove after establishing private bidirectional 1-1 message bus
                                                      #       where self.name should not be needed for message comms
        self.path               = os.path.dirname(os.path.realpath(__file__))
        self._GLADE_FILE        = f"{self.path}/favorites.glade"
        self._FAVORITES_FILE    = f"{self.path}/favorites.json"

        self._builder           = None
        self._event_system      = None
        self._event_sleep_time  = .5
        self._event_message     = None

        self._favorites_dialog  = None
        self._favorites_store   = None
        self._ui_objects        = None
        self._favorites         = None
        self._state             = None
        self._selected          = None


    def get_ui_element(self):
        button = Gtk.Button(label=self.name)
        button.connect("button-release-event", self._show_favorites_menu)
        return button

    def set_fm_event_system(self, fm_event_system):
        self._event_system = fm_event_system

    def set_ui_object_collection(self, ui_objects):
        self._ui_objects = ui_objects

    def run(self):
        self._module_event_observer()

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
        self._event_system.push_gui_event([self.name, "get_current_state", ()])
        self.wait_for_fm_message()

        self._state         = self._event_message
        self._event_message = None

    @threaded
    def _set_current_dir_lbl(self, widget=None, eve=None):
        self.wait_for_state()
        self._current_dir_lbl.set_label(f"Current Directory:\n{self._state.tab.get_current_directory()}")

    def _add_to_favorite(self, state):
        current_directory = self._state.tab.get_current_directory()
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



    def _show_favorites_menu(self, widget=None, eve=None):
        self._state = None
        self._get_state()
        self._set_current_dir_lbl()
        self._favorites_dialog.run()

    def _hide_favorites_menu(self, widget=None, eve=None):
        self._favorites_dialog.hide()

    def _set_selected(self, user_data):
        selected = user_data.get_selected()[1]
        if selected:
            self._selected = selected

    def wait_for_fm_message(self):
        while not self._event_message:
            pass

    def wait_for_state(self):
        while not self._state:
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
