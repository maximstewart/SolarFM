# Python imports

# Gtk imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Application imports


class ShowHideMixin:
    def show_messages_popup(self, type, text, seconds=None):
        self.message_popup_widget.popup()

    def show_plugins_popup(self, widget=None, eve=None):
        self.builder.get_object("plugin_controls").popup()

    def hide_plugins_popup(self, widget=None, eve=None):
        self.builder.get_object("plugin_controls").hide()

    def show_io_popup(self, widget=None, eve=None):
        self.builder.get_object("io_popup").popup()
