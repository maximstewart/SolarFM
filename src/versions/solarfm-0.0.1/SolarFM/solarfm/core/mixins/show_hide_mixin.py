# Python imports

# Gtk imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Application imports


class ShowHideMixin:
    def show_messages_popup(self, type, text, seconds=None):
        self.message_popup_widget.popup()

    def stop_file_searching(self, widget=None, eve=None):
        self.is_searching = False

    def show_appchooser_menu(self, widget=None, eve=None):
        appchooser_menu   = self.builder.get_object("appchooser_menu")
        appchooser_widget = self.builder.get_object("appchooser_widget")
        response          = appchooser_menu.run()

        if response == Gtk.ResponseType.OK:
            self.open_with_files(appchooser_widget)
            self.hide_appchooser_menu()

        if response == Gtk.ResponseType.CANCEL:
            self.hide_appchooser_menu()


    def hide_appchooser_menu(self, widget=None, eve=None):
        self.builder.get_object("appchooser_menu").hide()

    def run_appchooser_launch(self, widget=None, eve=None):
        dialog = widget.get_parent().get_parent()
        dialog.response(Gtk.ResponseType.OK)


    def show_plugins_popup(self, widget=None, eve=None):
        self.builder.get_object("plugin_controls").popup()

    def hide_plugins_popup(self, widget=None, eve=None):
        self.builder.get_object("plugin_controls").hide()

    def show_io_popup(self, widget=None, eve=None):
        self.builder.get_object("io_popup").popup()
