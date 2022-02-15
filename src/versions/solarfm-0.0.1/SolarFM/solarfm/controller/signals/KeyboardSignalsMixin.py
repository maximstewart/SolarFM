# Python imports
import re

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk

# Application imports


valid_keyvalue_pat    = re.compile(r"[a-z0-9A-Z-_\[\]\(\)\| ]")


class KeyboardSignalsMixin:
    def unset_keys_and_data(self, widget=None, eve=None):
        self.ctrlDown     = False
        self.shiftDown    = False
        self.altDown      = False
        self.is_searching = False

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


        if self.ctrlDown and self.shiftDown and keyname == "t":
            self.unset_keys_and_data()
            self.trash_files()


        if re.fullmatch(valid_keyvalue_pat, keyname):
            if not self.is_searching and not self.ctrlDown \
                and not self.shiftDown and not self.altDown:
                    focused_obj = self.window.get_focus()
                    if isinstance(focused_obj, Gtk.IconView):
                        self.is_searching = True
                        wid, tid, self.search_view, self.search_iconview, store = self.get_current_state()
                        self.unset_keys_and_data()
                        self.popup_search_files(wid, keyname)
                        return


        if (self.ctrlDown and keyname in ["1", "kp_1"]):
            self.builder.get_object("tggl_notebook_1").released()
        if (self.ctrlDown and keyname in ["2", "kp_2"]):
            self.builder.get_object("tggl_notebook_2").released()
        if (self.ctrlDown and keyname in ["3", "kp_3"]):
            self.builder.get_object("tggl_notebook_3").released()
        if (self.ctrlDown and keyname in ["4", "kp_4"]):
            self.builder.get_object("tggl_notebook_4").released()

        if self.ctrlDown and keyname == "q":
            self.tear_down()
        if (self.ctrlDown and keyname == "slash") or keyname == "home":
            self.builder.get_object("go_home").released()
        if (self.ctrlDown and keyname == "r") or keyname == "f5":
            self.builder.get_object("refresh_view").released()
        if (self.ctrlDown and keyname == "up") or (self.ctrlDown and keyname == "u"):
            self.builder.get_object("go_up").released()
        if self.ctrlDown and keyname == "l":
            self.unset_keys_and_data()
            self.builder.get_object("path_entry").grab_focus()
        if self.ctrlDown and keyname == "t":
            self.builder.get_object("create_tab").released()
        if self.ctrlDown and keyname == "o":
            self.unset_keys_and_data()
            self.open_files()
        if self.ctrlDown and keyname == "w":
            self.keyboard_close_tab()
        if self.ctrlDown and keyname == "h":
            self.show_hide_hidden_files()
        if (self.ctrlDown and keyname == "e"):
            self.unset_keys_and_data()
            self.rename_files()
        if self.ctrlDown and keyname == "c":
            self.copy_files()
            self.to_cut_files.clear()
        if self.ctrlDown and keyname == "x":
            self.to_copy_files.clear()
            self.cut_files()
        if self.ctrlDown and keyname == "v":
            self.paste_files()
        if self.ctrlDown and keyname == "n":
            self.unset_keys_and_data()
            self.show_new_file_menu()



        if keyname in ["alt_l", "alt_r"]:
            top_main_menubar = self.builder.get_object("top_main_menubar")
            if top_main_menubar.is_visible():
                top_main_menubar.hide()
            else:
                top_main_menubar.show()
        if keyname == "delete":
            self.unset_keys_and_data()
            self.delete_files()
        if keyname == "f2":
            self.unset_keys_and_data()
            self.rename_files()
        if keyname == "f4":
            self.unset_keys_and_data()
            self.open_terminal()
