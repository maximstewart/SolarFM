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
        self._plugin_list_widget  = self._settings.get_builder().get_object("plugin_list")
        self._plugin_list_socket  = self._settings.get_builder().get_object("plugin_socket")
        self._plugins_path        = self._settings.get_plugins_path()
        self._gtk_socket          = Gtk.Socket().new()
        self._plugins_dir_watcher = None
        self._plugin_collection   = []

        self._plugin_list_socket.add(self._gtk_socket)

        # NOTE: Must get ID after adding socket to window. Else issues....
        self._gtk_socket_id       = self._gtk_socket.get_id()
        self._plugin_list_widget.show_all()


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
                plugin = module.Main(self._gtk_socket_id, event_system)
                self._plugin_collection.append([file, plugin])

    def reload_plugins(self, file=None):
        print(f"Reloading plugins...")
        # if self._plugin_collection:
        #     to_unload = []
        #     for dir in self._plugin_collection:
        #         if not os.path.isdir(os.path.join(self._plugins_path, dir)):
        #             to_unload.append(dir)
