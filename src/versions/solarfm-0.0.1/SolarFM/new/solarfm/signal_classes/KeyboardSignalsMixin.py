# Python imports

# Gtk imports
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk

# Application imports


class KeyboardSignalsMixin:
    def global_key_press_controller(self, eve, user_data):
        keyname = Gdk.keyval_name(user_data.keyval).lower()
        if "control" in keyname or "alt" in keyname or "shift" in keyname:
            if "control" in keyname:
                self.ctrlDown    = True
            if "shift" in keyname:
                self.shiftDown   = True
            if "alt" in keyname:
                self.altDown     = True

    # NOTE: Yes, this should actually be mapped to some key controller setting
    #       file or something. Sue me.
    def global_key_release_controller(self, eve, user_data):
        keyname = Gdk.keyval_name(user_data.keyval).lower()
        if debug:
            print(f"global_key_release_controller > key > {keyname}")

        if "control" in keyname or "alt" in keyname or "shift" in keyname:
            if "control" in keyname:
                self.ctrlDown    = False
            if "shift" in keyname:
                self.shiftDown   = False
            if "alt" in keyname:
                self.altDown     = False

        if self.ctrlDown and keyname == "q":
            self.tear_down()
        if (self.ctrlDown and keyname == "slash") or keyname == "home":
            self.builder.get_object("go_home").released()
        if (self.ctrlDown and keyname == "r") or keyname == "f5":
            self.builder.get_object("refresh_view").released()
        if (self.ctrlDown and keyname == "up") or (self.ctrlDown and keyname == "u"):
            self.builder.get_object("go_up").released()
        if self.ctrlDown and keyname == "l":
            self.builder.get_object("path_entry").grab_focus()
        if self.ctrlDown and keyname == "t":
            self.builder.get_object("create_tab").released()
        if self.ctrlDown and keyname == "o":
            self.open_files()
        if self.ctrlDown and keyname == "w":
            self.keyboard_close_tab()
        if self.ctrlDown and keyname == "h":
            self.show_hide_hidden_files()
        if (self.ctrlDown and keyname == "e"):
            self.edit_files()
        if self.ctrlDown and keyname == "c":
            self.to_cut_files.clear()
            self.copy_files()
        if self.ctrlDown and keyname == "x":
            self.to_copy_files.clear()
            self.cut_files()
        if self.ctrlDown and keyname == "v":
            self.paste_files()
        if self.ctrlDown and keyname == "n":
            self.show_new_file_menu()

        if self.ctrlDown and self.shiftDown and keyname == "t":
            self.trash_files()
        if keyname == "delete":
            self.delete_files()
        if keyname == "f2":
            self.do_edit_files()
        if keyname == "f4":
            wid, tid = self.window_controller.get_active_data()
            view     = self.get_fm_window(wid).get_view_by_id(tid)
            dir      = view.get_current_directory()
            self.execute("terminator", dir)
