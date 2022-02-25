# Python imports
import sys, threading, subprocess, time

# Gtk imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Application imports


def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs, daemon=False).start()
    return wrapper


class Plugin:
    def __init__(self, builder, event_system):
        self._plugin_name  = "Example Plugin"
        self._builder      = builder
        self._event_system = event_system
        self._message      = None
        self._time_out     = 5

        button             = Gtk.Button(label=self._plugin_name)
        button.connect("button-release-event", self._do_action)

        plugin_list  = self._builder.get_object("plugin_socket")
        plugin_list.add(button)
        plugin_list.show_all()


    @threaded
    def _do_action(self, widget=None, eve=None):
        message = "Hello, World!"
        self._event_system.push_gui_event(["some_type", "display_message", ("warning", message, None)])


    def set_message(self, data):
        self._message = data

    def get_plugin_name(self):
        return self._plugin_name

    def get_socket_id(self):
        return self._socket_id

    def _run_timeout(self):
        timeout = 0
        while not self._message and timeout < self._time_out:
            time.sleep(1)
            timeout += 1
