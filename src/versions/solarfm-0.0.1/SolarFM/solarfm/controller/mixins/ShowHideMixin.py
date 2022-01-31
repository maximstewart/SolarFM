# Python imports

# Gtk imports
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk, Gio

# Application imports


class ShowHideMixin:
    def show_messages_popup(self, type, text, seconds=None):
        self.message_widget.popup()

    def stop_file_searching(self, widget=None, eve=None):
        self.is_searching = False

    def show_exists_page(self, widget=None, eve=None):
        response = self.file_exists_dialog.run()
        self.file_exists_dialog.hide()

        if response == Gtk.ResponseType.OK:
            return "rename"
        if response == Gtk.ResponseType.ACCEPT:
            return "rename_auto"
        if response == Gtk.ResponseType.CLOSE:
            return "rename_auto_all"
        if response == Gtk.ResponseType.YES:
            return "overwrite"
        if response == Gtk.ResponseType.APPLY:
            return "overwrite_all"
        if response == Gtk.ResponseType.NO:
            return "skip"
        if response == Gtk.ResponseType.REJECT:
            return "skip_all"

    def hide_exists_page_rename(self, widget=None, eve=None):
        self.file_exists_dialog.response(Gtk.ResponseType.OK)

    def hide_exists_page_auto_rename(self, widget=None, eve=None):
        self.file_exists_dialog.response(Gtk.ResponseType.ACCEPT)

    def hide_exists_page_auto_rename_all(self, widget=None, eve=None):
        self.file_exists_dialog.response(Gtk.ResponseType.CLOSE)


    def show_about_page(self, widget=None, eve=None):
        about_page = self.builder.get_object("about_page")
        response   = about_page.run()
        if (response == Gtk.ResponseType.CANCEL) or (response == Gtk.ResponseType.DELETE_EVENT):
            self.hide_about_page()

    def hide_about_page(self, widget=None, eve=None):
        self.builder.get_object("about_page").hide()


    def show_archiver_dialogue(self, widget=None, eve=None):
        wid, tid          = self.window_controller.get_active_data()
        view              = self.get_fm_window(wid).get_view_by_id(tid)
        archiver_dialogue = self.builder.get_object("archiver_dialogue")
        archiver_dialogue.set_action(Gtk.FileChooserAction.SAVE)
        archiver_dialogue.set_current_folder(view.get_current_directory())
        archiver_dialogue.set_current_name("arc.7z")

        response = archiver_dialogue.run()
        if response == Gtk.ResponseType.OK:
            self.archive_files(archiver_dialogue)
        if (response == Gtk.ResponseType.CANCEL) or (response == Gtk.ResponseType.DELETE_EVENT):
            pass

        archiver_dialogue.hide()

    def hide_archiver_dialogue(self, widget=None, eve=None):
        self.builder.get_object("archiver_dialogue").hide()


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
        self.builder.get_object("plugin_list").popup()

    def hide_plugins_popup(self, widget=None, eve=None):
        self.builder.get_object("plugin_list").hide()

    def show_context_menu(self, widget=None, eve=None):
        self.builder.get_object("context_menu").run()

    def hide_context_menu(self, widget=None, eve=None):
        self.builder.get_object("context_menu").hide()


    def show_new_file_menu(self, widget=None, eve=None):
        self.builder.get_object("context_menu_fname").set_text("")

        new_file_menu = self.builder.get_object("new_file_menu")
        response      = new_file_menu.run()
        if response == Gtk.ResponseType.APPLY:
            self.create_files()
        if response == Gtk.ResponseType.CANCEL:
            self.hide_new_file_menu()

    def hide_new_file_menu(self, widget=None, eve=None):
        self.builder.get_object("new_file_menu").hide()

    def show_edit_file_menu(self, widget=None, eve=None):
        if widget:
            widget.grab_focus()

        response = self.edit_file_menu.run()
        if response == Gtk.ResponseType.CLOSE:
            self.skip_edit   = True
        if response == Gtk.ResponseType.CANCEL:
            self.cancel_edit = True

    def hide_edit_file_menu(self, widget=None, eve=None):
        self.builder.get_object("edit_file_menu").hide()

    def hide_edit_file_menu_enter_key(self, widget=None, eve=None):
        keyname = Gdk.keyval_name(eve.keyval).lower()
        if "return" in keyname or "enter" in keyname:
            self.builder.get_object("edit_file_menu").hide()

    def hide_edit_file_menu_skip(self, widget=None, eve=None):
        self.edit_file_menu.response(Gtk.ResponseType.CLOSE)

    def hide_edit_file_menu_cancel(self, widget=None, eve=None):
        self.edit_file_menu.response(Gtk.ResponseType.CANCEL)
