# Python imports
import importlib

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
        self._plugins_dir_watcher = None
        self._socket              = Gtk.Socket().new()

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
            self.load_plugins(file)

    def load_plugins(self, file=None):
        print(f"(Re)loading plugins...")
        print(locals())

        # importlib.reload(stl_utils)
