# Python imports

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gio

# Application imports



class BottomStatusInfoException(Exception):
    ...



class BottomStatusInfoWidget:
    """docstring for BottomStatusInfoWidget."""

    def __init__(self):
        super(BottomStatusInfoWidget, self).__init__()

        _GLADE_FILE   = f"{settings.get_ui_widgets_path()}/bottom_status_info_ui.glade"
        self._builder = Gtk.Builder()
        self._builder.add_from_file(_GLADE_FILE)

        self._setup_styling()
        self._setup_signals()
        self._subscribe_to_events()
        self._load_widgets()


    def _setup_styling(self):
        ...

    def _setup_signals(self):
        ...

    def _subscribe_to_events(self):
        event_system.subscribe("set_bottom_labels", self.set_bottom_labels)

    def _load_widgets(self):
        builder = settings.get_builder()

        self.bottom_status_info      = self._builder.get_object("bottom_status_info")
        self.bottom_size_label       = self._builder.get_object("bottom_size_label")
        self.bottom_file_count_label = self._builder.get_object("bottom_file_count_label")
        self.bottom_path_label       = self._builder.get_object("bottom_path_label")

        builder.expose_object(f"bottom_status_info", self.bottom_status_info)
        builder.expose_object(f"bottom_size_label", self.bottom_size_label)
        builder.expose_object(f"bottom_file_count_label", self.bottom_file_count_label)
        builder.expose_object(f"bottom_path_label", self.bottom_path_label)

        builder.get_object("core_widget").add(self.bottom_status_info)


    def set_bottom_labels(self, tab):
        state                = event_system.emit_and_await("get_current_state")
        selected_files       = state.icon_grid.get_selected_items()
        current_directory    = tab.get_current_directory()
        path_file            = Gio.File.new_for_path(current_directory)
        mount_file           = path_file.query_filesystem_info(attributes="filesystem::*", cancellable=None)
        formatted_mount_free = sizeof_fmt( int(mount_file.get_attribute_as_string("filesystem::free")) )
        formatted_mount_size = sizeof_fmt( int(mount_file.get_attribute_as_string("filesystem::size")) )

        # NOTE: Hides empty trash and other desired buttons based on context.
        if settings.get_trash_files_path() == current_directory:
            event_system.emit("show_trash_buttons")
        else:
            event_system.emit("hide_trash_buttons")

        # If something selected
        self.bottom_size_label.set_label(f"{formatted_mount_free} free / {formatted_mount_size}")
        self.bottom_path_label.set_label(tab.get_current_directory())
        if selected_files:
            uris          = event_system.emit_and_await("format_to_uris", (state.store, state.wid, state.tid, selected_files, True))
            combined_size = 0
            for uri in uris:
                try:
                    file_info = Gio.File.new_for_path(uri).query_info(attributes="standard::size",
                                                        flags=Gio.FileQueryInfoFlags.NONE,
                                                        cancellable=None)
                    file_size = file_info.get_size()
                    combined_size += file_size
                except BottomStatusInfoException as e:
                    logger.debug(repr(e))

            formatted_size = sizeof_fmt(combined_size)
            if tab.is_hiding_hidden():
                self.bottom_path_label.set_label(f" {len(uris)} / {tab.get_files_count()} ({formatted_size})")
            else:
                self.bottom_path_label.set_label(f" {len(uris)} / {tab.get_not_hidden_count()} ({formatted_size})")

            return

        # If nothing selected
        if tab.is_hiding_hidden():
            if tab.get_hidden_count() > 0:
                self.bottom_file_count_label.set_label(f"{tab.get_not_hidden_count()} visible ({tab.get_hidden_count()} hidden)")
            else:
                self.bottom_file_count_label.set_label(f"{tab.get_files_count()} items")
        else:
            self.bottom_file_count_label.set_label(f"{tab.get_files_count()} items")
