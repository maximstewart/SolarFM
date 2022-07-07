# Python imports
import os, sys, importlib, traceback
from os.path import join, isdir

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio

# Application imports


class Plugin:
    path: str       = None
    name: str       = None
    author: str     = None
    version: str    = None
    suppoert: str   = None
    permissions:{}  = None
    reference: type = None



class Plugins:
    """Plugins controller"""

    def __init__(self, settings: type):
        self._settings            = settings
        self._builder             = self._settings.get_builder()
        self._plugins_path        = self._settings.get_plugins_path()
        self._plugins_dir_watcher = None
        self._plugin_collection   = []


    def launch_plugins(self) -> None:
        self._set_plugins_watcher()
        self.load_plugins()

    def _set_plugins_watcher(self) -> None:
        self._plugins_dir_watcher  = Gio.File.new_for_path(self._plugins_path) \
                                            .monitor_directory(Gio.FileMonitorFlags.WATCH_MOVES, Gio.Cancellable())
        self._plugins_dir_watcher.connect("changed", self._on_plugins_changed, ())

    def _on_plugins_changed(self, file_monitor, file, other_file=None, eve_type=None, data=None):
        if eve_type in [Gio.FileMonitorEvent.CREATED, Gio.FileMonitorEvent.DELETED,
                        Gio.FileMonitorEvent.RENAMED, Gio.FileMonitorEvent.MOVED_IN,
                                                    Gio.FileMonitorEvent.MOVED_OUT]:
            self.reload_plugins(file)

    def load_plugins(self, file: str = None) -> None:
        print(f"Loading plugins...")
        parent_path = os.getcwd()

        for file in os.listdir(self._plugins_path):
            try:
                path = join(self._plugins_path, file)
                if isdir(path):
                    module       = self.load_plugin_module(path, file)
                    plugin       = self.collect_info(module, path)
                    loading_data = self.parse_permissions(plugin)

                    self.execute_plugin(module, plugin, loading_data)
            except Exception as e:
                print("Malformed plugin! Not loading!")
                traceback.print_exc()

        os.chdir(parent_path)


    def load_plugin_module(self, path, file):
        os.chdir(path)
        sys.path.insert(0, path)
        spec   = importlib.util.spec_from_file_location(file, join(path, "plugin.py"))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        return module

    def collect_info(self, module, path) -> Plugin:
        plugin             = Plugin()
        plugin.path        = module.Manifest.path
        plugin.name        = module.Manifest.name
        plugin.author      = module.Manifest.author
        plugin.version     = module.Manifest.version
        plugin.support     = module.Manifest.support
        plugin.permissions = module.Manifest.permissions

        return plugin

    def parse_permissions(self, plugin):
        loading_data = {}
        permissions  = plugin.permissions
        keys         = permissions.keys()

        if "ui_target" in keys:
            if permissions["ui_target"] in  [
                                                "none", "other", "main_Window", "main_menu_bar", "path_menu_bar", "plugin_control_list",
                                                "context_menu", "window_1", "window_2", "window_3", "window_4"
                                            ]:
                if permissions["ui_target"] == "other":
                    if "ui_target_id" in keys:
                        loading_data["ui_target"] = self._builder.get_object(permissions["ui_target_id"])
                        if loading_data["ui_target"] == None:
                            raise Exception('Invalid "ui_target_id" given in permissions. Must have one if setting "ui_target" to "other"...')
                    else:
                        raise Exception('Invalid "ui_target_id" given in permissions. Must have one if setting "ui_target" to "other"...')
                else:
                    loading_data["ui_target"] = self._builder.get_object(permissions["ui_target"])
            else:
                raise Exception('Unknown "ui_target" given in permissions.')


        if "pass_fm_events" in keys:
            if permissions["pass_fm_events"] in ["true"]:
                loading_data["pass_fm_events"] = True

        return loading_data

    def execute_plugin(self, module: type, plugin: Plugin, loading_data: []):
        plugin.reference = module.Plugin()
        keys             = loading_data.keys()

        if "ui_target" in keys:
            loading_data["ui_target"].add(plugin.reference.get_ui_element())
            loading_data["ui_target"].show_all()

        if "pass_fm_events" in keys:
            plugin.reference.set_fm_event_system(event_system)

        plugin.reference.run()
        self._plugin_collection.append(plugin)

    def reload_plugins(self, file: str = None) -> None:
        print(f"Reloading plugins... stub.")
