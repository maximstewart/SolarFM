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
        self.start_loop()

    @threaded
    def start_loop(self):
        i      = 0
        cycles = 5
        alive  = True
        while alive:
            if i == cycles:
                alive = False

            self._event_system.push_gui_event(["some_type", "display_message", ("warning", str(i), None)])
            i += 1

            time.sleep(1)
