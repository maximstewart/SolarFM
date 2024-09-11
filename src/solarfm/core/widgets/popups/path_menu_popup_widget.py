# Python imports

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Application imports




class PathMenuPopupWidget(Gtk.Popover):
    """docstring for PathMenuPopupWidget."""

    def __init__(self):
        super(PathMenuPopupWidget, self).__init__()

        self.builder = settings_manager.get_builder()
        self.builder.expose_object(f"path_menu", self)

        self._setup_styling()
        self._setup_signals()
        self._load_widgets()


    def _setup_styling(self):
        path_entry = self.builder.get_object(f"path_entry")
        self.set_relative_to(path_entry)
        self.set_modal(False)
        self.set_position(Gtk.PositionType.BOTTOM)
        self.set_size_request(480, 420)

    def _setup_signals(self):
        event_system.subscribe("show_path_menu", self.show_path_menu)
        event_system.subscribe("hide_path_menu", self.hide_path_menu)

    def _load_widgets(self):
        scroll_window     = Gtk.ScrolledWindow()
        view_port         = Gtk.Viewport()
        path_menu_buttons = Gtk.Box()

        scroll_window.set_vexpand(True)
        scroll_window.set_hexpand(True)
        path_menu_buttons.set_orientation(Gtk.Orientation.VERTICAL)

        self.builder.expose_object(f"path_menu_buttons", path_menu_buttons)
        view_port.add(path_menu_buttons)
        scroll_window.add(view_port)
        self.add(scroll_window)

        scroll_window.show_all()


    def show_path_menu(self, widget = None, eve = None):
        self.popup()

    def hide_path_menu(self, widget = None, eve = None):
        self.popdown()