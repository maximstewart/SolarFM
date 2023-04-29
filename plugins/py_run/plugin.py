# Python imports
import os
import threading
import subprocess

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

        self.name        = "PyRun"  # NOTE: Need to remove after establishing private bidirectional 1-1 message bus
                                    #       where self.name should not be needed for message comms


    def run(self):
        ...

    def generate_reference_ui_element(self):
        button = Gtk.Button(label=self.name)
        button.connect("button-release-event", self.start_run)
        button.set_image( Gtk.Image(stock=Gtk.STOCK_MEDIA_PLAY ) )
        button.set_always_show_image(True)
        return button

    def start_run(self, widget=None, eve=None):
        self._event_system.emit("get_current_state")
        state       = self._fm_state
        current_dir = state.tab.get_current_directory()
        isValid     = False
        command     = ["terminator", "-x", f"bash -c 'python . && bash'"]

        if not state.uris:
            for file in os.listdir(current_dir):
                path = os.path.join(current_dir, file)
                if os.path.isfile(path) and file == "__main__.py":
                    isValid = True
                    break
        elif state.uris and len(state.uris) == 1:
                file = state.uris[0]
                if os.path.isfile(file) and file.endswith(".py"):
                    command = ["terminator", "-x", f"bash -c 'python {state.uris[0]} && bash'"]
                    isValid = True

        if isValid:
            self.launch(current_dir, command)

    def launch(self, current_dir = "/", command = []):
        subprocess.Popen(command, cwd=current_dir, shell=False, start_new_session=True, stdout=None, stderr=None, close_fds=True)
