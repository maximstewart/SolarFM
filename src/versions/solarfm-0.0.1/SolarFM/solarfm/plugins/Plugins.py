# Python imports
import os, importlib
from os.path import join, isdir

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio

# Application imports




class Plugins:
    """docstring for Plugins"""
    def __init__(self, settings):
        self._settings            = settings
        self._plugins_path        = self._settings.get_plugins_path()
        self._socket              = Gtk.Socket().new()
        self._plugins_dir_watcher = None
        self._socket_id           = None
        self._plugin_collection   = []

        self._settings.get_main_window().add(self._socket)
        self._socket.show()
        self._socket_id = self._socket.get_id()


    def launch_plugins(self):
        self._set_plugins_watcher()
        self.load_plugins()

    def _set_plugins_watcher(self):
        self._plugins_dir_watcher  = Gio.File.new_for_path(self._plugins_path) \
                                            .monitor_directory(Gio.FileMonitorFlags.WATCH_MOVES, Gio.Cancellable())
        self._plugins_dir_watcher.connect("changed", self._on_plugins_changed, ())

    def _on_plugins_changed(self, file_monitor, file, other_file=None, eve_type=None, data=None):
        if eve_type in [Gio.FileMonitorEvent.CREATED, Gio.FileMonitorEvent.DELETED,
                        Gio.FileMonitorEvent.RENAMED, Gio.FileMonitorEvent.MOVED_IN,
                                                    Gio.FileMonitorEvent.MOVED_OUT]:
            self.reload_plugins(file)

    def load_plugins(self, file=None):
        print(f"Loading plugins...")
        for file in os.listdir(self._plugins_path):
            path = join(self._plugins_path, file)
            if isdir(path):
                spec   = importlib.util.spec_from_file_location(file, join(path, "__main__.py"))
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                self._plugin_collection.append([file, module])
                # module.set_socket_id(self._socket_id)
                # print(f"\n\n\n {event_system} \n\n\n")
                # module.set_event_system(event_system)
                # module.main()
                # module.start_loop(event_system)

        print(self._plugin_collection)

    def reload_plugins(self, file=None):
        print(f"Reloading plugins...")
        if self._plugin_collection:
            to_unload = []
            for dir in self._plugin_collection:
                if not os.path.isdir(os.path.join(self._plugins_path, dir)):
                    to_unload.append(dir)
