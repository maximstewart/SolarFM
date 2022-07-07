# Python imports
import os, threading, subprocess, time

# Gtk imports
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




class Manifest:
    path: str        = os.path.dirname(os.path.realpath(__file__))
    name: str        = "Youtube Download"
    author: str      = "ITDominator"
    version: str     = "0.0.1"
    support: str     = ""
    permissions: {}  = {
        'ui_target': "plugin_control_list",
        'pass_fm_events': "true"

    }


class Plugin(Manifest):
    def __init__(self):
        self._fm_event_system   = None
        self._event_sleep_time  = .5
        self._fm_event_message  = None


    def get_ui_element(self):
        button = Gtk.Button(label=self.name)
        button.connect("button-release-event", self._do_download)
        return button

    def set_fm_event_system(self, fm_event_system):
        self._fm_event_system = fm_event_system

    def run(self):
        self._module_event_observer()


    @daemon_threaded
    def _module_event_observer(self):
        while True:
            time.sleep(self._event_sleep_time)
            event = self._fm_event_system.read_module_event()
            if event:
                try:
                    if event[0] is self.name:
                        target_id, method_target, data = self._fm_event_system.consume_module_event()

                        if not method_target:
                            self._fm_event_message = data
                        else:
                            method = getattr(self.__class__, f"{method_target}")
                            data   = method(*(self, *parameters))
                except Exception as e:
                    print(repr(e))


    @threaded
    def _do_download(self, widget=None, eve=None):
        self._fm_event_system.push_gui_event([self.name, "get_current_state", ()])
        while not self._fm_event_message:
            pass

        state = self._fm_event_message
        subprocess.Popen([f'{self.path}/download.sh' , state.tab.get_current_directory()])
        self._fm_event_message = None
