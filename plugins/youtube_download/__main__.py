# Python imports
import os, sys, threading, subprocess, time

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
        self._plugin_name  = "Youtube Download"
        self._builder      = builder
        self._event_system = event_system
        self._message      = None
        self._time_out     = 5

        self.SCRIPT_PTH    = os.path.dirname(os.path.realpath(__file__))

        button             = Gtk.Button(label=self._plugin_name)
        button.connect("button-release-event", self._do_download)

        plugin_list  = self._builder.get_object("plugin_socket")
        plugin_list.add(button)
        plugin_list.show_all()


    @threaded
    def _do_download(self, widget=None, eve=None):
        self._event_system.push_gui_event([self._plugin_name, "get_current_state", ()])
        self._run_timeout()

        if self._message:
            wid, tid, view, iconview, store = self._message
            subprocess.Popen([f'{self.SCRIPT_PTH}/download.sh' , view.get_current_directory()])
            self._message = None


    def set_message(self, data):
        self._message = data

    def get_plugin_name(self):
        return self._plugin_name

    def _run_timeout(self):
        timeout = 0
        while not self._message and timeout < self._time_out:
            time.sleep(1)
            timeout += 1
