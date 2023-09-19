# Python imports

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Application imports




class IOPopupWidget(Gtk.Popover):
    """docstring for IOPopupWidget."""

    def __init__(self):
        super(IOPopupWidget, self).__init__()

        self._builder = settings_manager.get_builder()
        self._builder.expose_object(f"io_popup", self)

        self._setup_styling()
        self._setup_signals()
        self._load_widgets()


    def _setup_styling(self):
        io_button = self._builder.get_object(f"io_button")
        self.set_relative_to(io_button)
        self.set_modal(True)
        self.set_position(Gtk.PositionType.BOTTOM)
        self.set_size_request(320, 280)

    def _setup_signals(self):
        event_system.subscribe("show_io_popup", self.show_io_popup)

    def _load_widgets(self):
        vbox = Gtk.Box()

        vbox.set_orientation(Gtk.Orientation.VERTICAL)
        self._builder.expose_object(f"io_list", vbox)
        self.add(vbox)


    def show_io_popup(self, widget=None, eve=None):
        self.popup()
