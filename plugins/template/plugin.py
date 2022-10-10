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

        self.name               = "Example Plugin"  # NOTE: Need to remove after establishing private bidirectional 1-1 message bus
                                                    #       where self.name should not be needed for message comms


    def generate_reference_ui_element(self):
        button = Gtk.Button(label=self.name)
        button.connect("button-release-event", self.send_message)
        return button

    def run(self):
        ...

    def send_message(self, widget=None, eve=None):
        message = "Hello, World!"
        event_system.emit("display_message", ("warning", message, None))
