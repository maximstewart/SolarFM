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


    def show_exists_page(self, widget=None, eve=None):
        # self.exists_alert       = self.builder.get_object("exists_alert")
        # self.exists_from_label  = self.builder.get_object("exists_from_label")
        # self.exists_to_label    = self.builder.get_object("exists_to_label")
        # self.exists_file_field  = self.builder.get_object("exists_file_field")


        response = self.exists_alert.run()
        if response == Gtk.ResponseType.OK:      # Rename
            print(response)
            return "rename", Gio.FileCreateFlags.NONE
        if response == Gtk.ResponseType.ACCEPT:  # Auto rename
            return "rename_auto", Gio.FileCreateFlags.NONE
        if response == Gtk.ResponseType.CLOSE:   # Auto rename all
            return "rename_auto_all", Gio.FileCreateFlags.NONE
        if response == Gtk.ResponseType.YES:     # Overwrite
            return "overwrite", Gio.FileCreateFlags.OVERWRITE
        if response == Gtk.ResponseType.APPLY:   # Overwrite all
            return "overwrite_all", Gio.FileCreateFlags.OVERWRITE
        if response == Gtk.ResponseType.NO:      # Skip
            return "skip", Gio.FileCreateFlags.NONE
        if response == Gtk.ResponseType.CANCEL:  # Skip all
            return "skip_all", Gio.FileCreateFlags.NONE



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

        if response == Gtk.ResponseType.CANCEL:
            self.hide_appchooser_menu()
        if response == Gtk.ResponseType.OK:
            self.open_with_files(appchooser_widget)
            self.hide_appchooser_menu()

    def hide_appchooser_menu(self, widget=None, eve=None):
        self.builder.get_object("appchooser_menu").hide()

    def run_appchooser_launch(self, widget=None, eve=None):
        dialog = widget.get_parent().get_parent()
        dialog.response(Gtk.ResponseType.OK)

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
        if widget:
            name = widget.get_name()
            if name == "rename":
                self.builder.get_object("edit_file_menu").hide()
            else:
                keyname = Gdk.keyval_name(eve.keyval).lower()
                if "return" in keyname or "enter" in keyname:
                    self.builder.get_object("edit_file_menu").hide()


    def hide_edit_file_menu_skip(self, widget=None, eve=None):
        self.skip_edit   = True
        self.builder.get_object("edit_file_menu").hide()

    def hide_edit_file_menu_cancel(self, widget=None, eve=None):
        self.cancel_edit = True
        self.builder.get_object("edit_file_menu").hide()
