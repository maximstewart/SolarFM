# Python imports

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Application imports




class PluginsPopupWidget(Gtk.Popover):
    """docstring for PluginsPopupWidget."""

    def __init__(self):
        super(PluginsPopupWidget, self).__init__()

        self.builder = settings.get_builder()
        self.builder.expose_object(f"plugin_controls", self)

        self._setup_styling()
        self._setup_signals()
        self._load_widgets()


    def _setup_styling(self):
        plugins_button = self.builder.get_object(f"plugins_button")
        self.set_relative_to(plugins_button)
        self.set_modal(True)
        self.set_position(Gtk.PositionType.BOTTOM)

    def _setup_signals(self):
        event_system.subscribe("show_plugins_popup", self.show_plugins_popup)
        self.connect("button-release-event", self.hide_plugins_popup)
        self.connect("key-release-event", self.hide_plugins_popup)

    def _load_widgets(self):
        vbox = Gtk.Box()

        vbox.set_orientation(Gtk.Orientation.VERTICAL)
        self.builder.expose_object(f"plugin_control_list", vbox)
        self.add(vbox)


    def show_plugins_popup(self, widget=None, eve=None):
        self.popup()

    def hide_plugins_popup(self, widget=None, eve=None):
        self.hide()
