# Python imports
import sys, traceback, threading, inspect, os, time

# Gtk imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Application imports


def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs, daemon=True).start()
    return wrapper


class Main:
    def __init__(self, socket_id, event_system):
        self._socket_id    = socket_id
        self._event_system = event_system
        self._gtk_plug     = Gtk.Plug.new(self._socket_id)

        button = Gtk.Button(label="Click Me!")
        button.connect("button-release-event", self._do_action)
        self._gtk_plug.add(button)
        self._gtk_plug.show_all()


    def _do_action(self, widget=None, eve=None):
        message = "Hello, World!"
        self._event_system.push_gui_event(["some_type", "display_message", ("warning", message, None)])


    def get_socket_id(self):
        return self._socket_id
