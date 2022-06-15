# Python imports
import os, threading, subprocess, time

# Gtk imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Application imports


# NOTE: Threads will not die with parent's destruction
def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs, daemon=False).start()
    return wrapper

# NOTE: Insure threads die with parent's destruction
def daemon_threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs, daemon=True).start()
    return wrapper




class Plugin:
    def __init__(self, builder, event_system):
        self.SCRIPT_PTH         = os.path.dirname(os.path.realpath(__file__))
        self._plugin_name       = "Example Plugin"
        self._plugin_author     = "John Doe"
        self._plugin_version    = "0.0.1"

        self._builder           = builder
        self._event_system      = event_system
        self._event_sleep_time  = .5
        self._event_message     = None

        button = Gtk.Button(label=self._plugin_name)
        button.connect("button-release-event", self.send_message)

        # self._module_event_observer()  # NOTE: Enable if you want the plugin to watch for events sent to it

        plugin_list = self._builder.get_object("plugin_socket")
        plugin_list.add(button)
        plugin_list.show_all()


    def send_message(self, widget=None, eve=None):
        message = "Hello, World!"
        self._event_system.push_gui_event([self._plugin_name, "display_message", ("warning", message, None)])


    def get_plugin_name(self):
        return self._plugin_name

    def get_plugin_author(self):
        return self._plugin_author

    def get_plugin_version(self):
        return self._plugin_version

    def get_socket_id(self):
        return self._socket_id

    @daemon_threaded
    def _module_event_observer(self):
        while True:
            time.sleep(self._event_sleep_time)
            event = self._event_system.read_module_event()
            if event:
                try:
                    if event[0] is self._plugin_name:
                        target_id, method_target, data = self._event_system.consume_module_event()

                        if not method_target:
                            self._event_message = data
                        else:
                            method = getattr(self.__class__, f"{method_target}")
                            data   = method(*(self, *parameters))
                except Exception as e:
                    print(repr(e))
