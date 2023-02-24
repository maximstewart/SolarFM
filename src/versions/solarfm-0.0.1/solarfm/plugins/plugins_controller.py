# Python imports
import os
import sys
import importlib
import traceback
from os.path import join
from os.path import isdir

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gio

# Application imports
from .manifest import PluginInfo
from .manifest import ManifestProcessor




class InvalidPluginException(Exception):
    ...


class PluginsController:
    """PluginsController controller"""

    def __init__(self):
        path                      = os.path.dirname(os.path.realpath(__file__))
        sys.path.insert(0, path)  # NOTE: I think I'm not using this correctly...

        self._builder             = settings.get_builder()
        self._plugins_path        = settings.get_plugins_path()

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
        logger.info(f"Loading plugins...")
        parent_path = os.getcwd()

        for path, folder in [[join(self._plugins_path, item), item] if os.path.isdir(join(self._plugins_path, item)) else None for item in os.listdir(self._plugins_path)]:
            try:
                target   = join(path, "plugin.py")
                manifest = ManifestProcessor(path, self._builder)

                if not os.path.exists(target):
                    raise FileNotFoundError("Invalid Plugin Structure: Plugin doesn't have 'plugin.py'. Aboarting load...")

                plugin, loading_data = manifest.get_loading_data()
                module               = self.load_plugin_module(path, folder, target)
                self.execute_plugin(module, plugin, loading_data)
            except InvalidPluginException as e:
                logger.info(f"Malformed Plugin: Not loading -->: '{folder}' !")
                logger.debug("Trace: ", traceback.print_exc())

        os.chdir(parent_path)


    def load_plugin_module(self, path, folder, target):
        os.chdir(path)

        locations = []
        self.collect_search_locations(path, locations)

        spec   = importlib.util.spec_from_file_location(folder, target, submodule_search_locations = locations)
        module = importlib.util.module_from_spec(spec)
        sys.modules[folder] = module
        spec.loader.exec_module(module)

        return module

    def collect_search_locations(self, path, locations):
        locations.append(path)
        for file in os.listdir(path):
            _path = os.path.join(path, file)
            if os.path.isdir(_path):
                self.collect_search_locations(_path, locations)

    def execute_plugin(self, module: type, plugin: PluginInfo, loading_data: []):
        plugin.reference = module.Plugin()
        keys             = loading_data.keys()

        if "ui_target" in keys:
            loading_data["ui_target"].add( plugin.reference.generate_reference_ui_element() )
            loading_data["ui_target"].show_all()

        if "pass_ui_objects" in keys:
            plugin.reference.set_ui_object_collection( loading_data["pass_ui_objects"] )

        if "pass_fm_events" in keys:
            plugin.reference.set_fm_event_system(event_system)
            plugin.reference.subscribe_to_events()

        if "bind_keys" in keys:
            keybindings.append_bindings( loading_data["bind_keys"] )

        plugin.reference.run()
        self._plugin_collection.append(plugin)

    def reload_plugins(self, file: str = None) -> None:
        logger.info(f"Reloading plugins...")
        parent_path = os.getcwd()

        for plugin in self._plugin_collection:
            os.chdir(plugin.path)
            plugin.reference.reload_package(f"{plugin.path}/plugin.py")

        os.chdir(parent_path)
