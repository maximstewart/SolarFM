# Python imports

# Lib imports
import gi
from gi.repository import Gio

# Application imports



class PluginReloadMixin:
    _plugins_dir_watcher = None

    def _set_plugins_watcher(self) -> None:
        self._plugins_dir_watcher = Gio.File.new_for_path(
                                        self._plugins_path
                                    ).monitor_directory(
                                        Gio.FileMonitorFlags.WATCH_MOVES,
                                        Gio.Cancellable()
                                    )

        self._plugins_dir_watcher.connect("changed", self._on_plugins_changed, ())

    def _on_plugins_changed(self,
        file_monitor, file,
        other_file = None,
        eve_type   = None,
        data       = None
    ):
        if eve_type in [Gio.FileMonitorEvent.CREATED, Gio.FileMonitorEvent.DELETED,
                        Gio.FileMonitorEvent.RENAMED, Gio.FileMonitorEvent.MOVED_IN,
                                                      Gio.FileMonitorEvent.MOVED_OUT]:
            self.reload_plugins(file)

    def reload_plugins(self, file: str = None) -> None:
        logger.info(f"Reloading plugins... stub.")
