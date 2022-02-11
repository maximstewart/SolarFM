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
    gtk_socket_id = None
    gtk_socket    = None
    reference     = None


class Plugins:
    """docstring for Plugins"""
    def __init__(self, settings):
        self._settings            = settings
        self._plugin_list_widget  = self._settings.get_builder().get_object("plugin_list")
        self._plugin_list_socket  = self._settings.get_builder().get_object("plugin_socket")
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

                    gtk_socket    = Gtk.Socket().new()
                    self._plugin_list_socket.add(gtk_socket)
                    # NOTE: Must get ID after adding socket to window. Else issues....
                    gtk_socket_id = gtk_socket.get_id()

                    sys.path.insert(0, path)
                    spec          = importlib.util.spec_from_file_location(file, join(path, "__main__.py"))
                    module        = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    ref                  = module.Main(gtk_socket_id, event_system)
                    plugin               = Plugin()
                    plugin.name          = ref.get_plugin_name()
                    plugin.module        = path
                    plugin.gtk_socket_id = gtk_socket_id
                    plugin.gtk_socket    = gtk_socket
                    plugin.reference     = ref

                    self._plugin_collection.append(plugin)
                    gtk_socket.show_all()
            except Exception as e:
                print("Malformed plugin! Not loading!")
                traceback.print_exc()

        os.chdir(parent_path)


    def reload_plugins(self, file=None):
        print(f"Reloading plugins...")
        # if self._plugin_collection:
        #     to_unload = []
        #     for dir in self._plugin_collection:
        #         if not os.path.isdir(os.path.join(self._plugins_path, dir)):
        #             to_unload.append(dir)

    def set_message_on_plugin(self, type, data):
        print("Trying to send message to plugin...")
        for plugin in self._plugin_collection:
            if type in plugin.name:
                print('Found plugin; posting message...')
                plugin.reference.set_message(data)
