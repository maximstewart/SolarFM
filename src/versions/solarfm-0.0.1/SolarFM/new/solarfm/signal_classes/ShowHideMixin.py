# Python imports

# Gtk imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Application imports


class ShowHideMixin:
    def show_messages_popup(self, type, text, seconds=None):
        self.message_widget.popup()

    def show_about_page(self, widget=None, eve=None):
        about_page = self.builder.get_object("about_page")
        response   = about_page.run()
        if (response == Gtk.ResponseType.CANCEL) or (response == Gtk.ResponseType.DELETE_EVENT):
            self.hide_about_page()

    def hide_about_page(self, widget=None, eve=None):
        about_page = self.builder.get_object("about_page").hide()

    def show_appchooser_menu(self, widget=None, eve=None):
        appchooser_menu   = self.builder.get_object("appchooser_menu")
        appchooser_widget = self.builder.get_object("appchooser_widget")

        resp = appchooser_menu.run()
        if resp == Gtk.ResponseType.CANCEL:
            self.hide_appchooser_menu()
        if resp == Gtk.ResponseType.OK:
            self.open_with_files(appchooser_widget)
            self.hide_appchooser_menu()

    def hide_appchooser_menu(self, widget=None, eve=None):
        self.builder.get_object("appchooser_menu").hide()

    def run_appchooser_launch(self, widget=None, eve=None):
        self.builder.get_object("appchooser_select_btn").pressed()

    def show_context_menu(self, widget=None, eve=None):
        self.builder.get_object("context_menu").run()

    def hide_context_menu(self, widget=None, eve=None):
        self.builder.get_object("context_menu").hide()

    def show_new_file_menu(self, widget=None, eve=None):
        self.builder.get_object("new_file_menu").run()

    def hide_new_file_menu(self, widget=None, eve=None):
        self.builder.get_object("new_file_menu").hide()

    def show_edit_file_menu(self, widget=None, eve=None):
        self.builder.get_object("edit_file_menu").run()

    def hide_edit_file_menu(self, widget=None, eve=None):
        self.builder.get_object("edit_file_menu").hide()

    def hide_edit_file_menu_skip(self, widget=None, eve=None):
        self.skip_edit   = True
        self.builder.get_object("edit_file_menu").hide()

    def hide_edit_file_menu_cancel(self, widget=None, eve=None):
        self.cancel_edit = True
        self.builder.get_object("edit_file_menu").hide()
