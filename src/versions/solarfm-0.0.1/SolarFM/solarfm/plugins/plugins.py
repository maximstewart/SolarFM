# Python imports
import os, sys, importlib, traceback
from os.path import join, isdir

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio

# Application imports
from .manifest import Plugin, ManifestProcessor




class Plugins:
    """Plugins controller"""

    def __init__(self, settings: type):
        self._settings            = settings
        self._builder             = self._settings.get_builder()
        self._plugins_path        = self._settings.get_plugins_path()
        self._keybindings         = self._settings.get_keybindings()

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

        for path, folder in [[join(self._plugins_path, item), item] if os.path.isdir(join(self._plugins_path, item)) else None for item in os.listdir(self._plugins_path)]:
            try:
                target   = join(path, "plugin.py")
                manifest = ManifestProcessor(path, self._builder)

                if not os.path.exists(target):
                    raise Exception("Invalid Plugin Structure: Plugin doesn't have 'plugin.py'. Aboarting load...")

                plugin, loading_data = manifest.get_loading_data()
                module               = self.load_plugin_module(path, folder, target)
                self.execute_plugin(module, plugin, loading_data)
            except Exception as e:
                print(f"Malformed Plugin: Not loading -->: '{folder}' !")
                traceback.print_exc()

        os.chdir(parent_path)


    def load_plugin_module(self, path, folder, target):
        os.chdir(path)
        sys.path.insert(0, path)  # NOTE: I think I'm not using this correctly...
        # The folder and target aren't working to create parent package references, so using as stopgap.
        # The above is probably polutling import logic and will cause unforseen import issues.
        spec   = importlib.util.spec_from_file_location(folder, target)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        return module


    def execute_plugin(self, module: type, plugin: Plugin, loading_data: []):
        plugin.reference = module.Plugin()
        keys             = loading_data.keys()

        if "ui_target" in keys:
            loading_data["ui_target"].add( plugin.reference.get_ui_element() )
            loading_data["ui_target"].show_all()

        if "pass_ui_objects" in keys:
            plugin.reference.set_ui_object_collection( loading_data["pass_ui_objects"] )

        if "pass_fm_events" in keys:
            plugin.reference.set_fm_event_system(event_system)

        if "bind_keys" in keys:
            self._keybindings.append_bindings( loading_data["bind_keys"] )

        plugin.reference.run()
        self._plugin_collection.append(plugin)

    def reload_plugins(self, file: str = None) -> None:
        print(f"Reloading plugins... stub.")
