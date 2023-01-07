# Python imports
import os, threading, subprocess, time

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Application imports
from plugins.plugin_base import PluginBase


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

        self.path              = os.path.dirname(os.path.realpath(__file__))
        self.name              = "Git Clone"  # NOTE: Need to remove after establishing private bidirectional 1-1 message bus
                                              #       where self.name should not be needed for message comms

    def generate_reference_ui_element(self):
        button = Gtk.Button(label=self.name)
        button.connect("button-release-event", self._do_download)
        return button

    def run(self):
        ...


    def _do_download(self, widget=None, eve=None):
        self._event_system.emit("get_current_state")

        dir = self._fm_state.tab.get_current_directory()
        self._download(dir)

    @threaded
    def _download(self, dir):
        subprocess.Popen([f'{self.path}/download.sh', dir])
