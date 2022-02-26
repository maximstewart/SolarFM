# Python imports
import os, sys, importlib, traceback
from os.path import join, isdir

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio

# Application imports


class Plugin:
    name          = None
    module        = None
    reference     = None


class Plugins:
    """Plugins controller"""

    def __init__(self, settings):
        self._settings            = settings
        self._builder             = self._settings.get_builder()
        self._plugins_path        = self._settings.get_plugins_path()
        self._plugins_dir_watcher = None
        self._plugin_collection   = []


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

    # @threaded
    def load_plugins(self, file=None):
        print(f"Loading plugins...")
        parent_path = os.getcwd()

        for file in os.listdir(self._plugins_path):
            try:
                path = join(self._plugins_path, file)
                if isdir(path):
                    os.chdir(path)

                    sys.path.insert(0, path)
                    spec = importlib.util.spec_from_file_location(file, join(path, "__main__.py"))
                    app  = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(app)

                    plugin_reference = app.Plugin(self._builder, event_system)
                    plugin           = Plugin()
                    plugin.name      = plugin_reference.get_plugin_name()
                    plugin.module    = path
                    plugin.reference = plugin_reference

                    self._plugin_collection.append(plugin)
            except Exception as e:
                print("Malformed plugin! Not loading!")
                traceback.print_exc()

        os.chdir(parent_path)


    def reload_plugins(self, file=None):
        print(f"Reloading plugins... stub.")

    def send_message_to_plugin(self, type, data):
        print("Trying to send message to plugin...")
        for plugin in self._plugin_collection:
            if type in plugin.name:
                print('Found plugin; posting message...')
                plugin.reference.set_message(data)
