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
    """ KeyboardSignalsMixin keyboard hooks controller. """

    def unset_keys_and_data(self, widget=None, eve=None):
        self.ctrl_down    = False
        self.shift_down   = False
        self.alt_down     = False
        self.is_searching = False

    def global_key_press_controller(self, eve, user_data):
        keyname = Gdk.keyval_name(user_data.keyval).lower()
        if keyname.replace("_l", "").replace("_r", "") in ["control", "alt", "shift"]:
            if "control" in keyname:
                self.ctrl_down    = True
            if "shift" in keyname:
                self.shift_down   = True
            if "alt" in keyname:
                self.alt_down     = True

    # NOTE: Yes, this should actually be mapped to some key controller setting
    #       file or something. Sue me.
    def global_key_release_controller(self, eve, user_data):
        keyname = Gdk.keyval_name(user_data.keyval).lower()
        if debug:
            print(f"global_key_release_controller > key > {keyname}")

        if keyname.replace("_l", "").replace("_r", "") in ["control", "alt", "shift"]:
            if "control" in keyname:
                self.ctrl_down    = False
            if "shift" in keyname:
                self.shift_down   = False
            if "alt" in keyname:
                self.alt_down     = False

        if self.ctrl_down and self.shift_down and keyname == "t":
            self.unset_keys_and_data()
            self.trash_files()

        if self.ctrl_down:
            if keyname in ["1", "kp_1", "2", "kp_2", "3", "kp_3", "4", "kp_4"]:
                self.builder.get_object(f"tggl_notebook_{keyname.strip('kp_')}").released()
            if keyname == "q":
                self.tear_down()
            if keyname == "slash" or keyname == "home":
                self.builder.get_object("go_home").released()
            if keyname == "r" or keyname == "f5":
                self.builder.get_object("refresh_tab").released()
            if keyname == "up" or keyname == "u":
                self.builder.get_object("go_up").released()
            if keyname == "l":
                self.unset_keys_and_data()
                self.builder.get_object("path_entry").grab_focus()
            if keyname == "t":
                self.builder.get_object("create_tab").released()
            if keyname == "o":
                self.unset_keys_and_data()
                self.open_files()
            if keyname == "w":
                self.keyboard_close_tab()
            if keyname == "h":
                self.show_hide_hidden_files()
            if keyname == "e":
                self.unset_keys_and_data()
                self.rename_files()
            if keyname == "c":
                self.copy_files()
                self.to_cut_files.clear()
            if keyname == "x":
                self.to_copy_files.clear()
                self.cut_files()
            if keyname == "v":
                self.paste_files()
            if keyname == "n":
                self.unset_keys_and_data()
                self.show_new_file_menu()

        if keyname == "delete":
            self.unset_keys_and_data()
            self.delete_files()
        if keyname == "f2":
            self.unset_keys_and_data()
            self.rename_files()
        if keyname == "f4":
            self.unset_keys_and_data()
            self.open_terminal()
        if keyname in ["alt_l", "alt_r"]:
            top_main_menubar = self.builder.get_object("top_main_menubar")
            top_main_menubar.hide() if top_main_menubar.is_visible() else top_main_menubar.show()

        if re.fullmatch(valid_keyvalue_pat, keyname):
            if not self.is_searching and not self.ctrl_down \
                and not self.shift_down and not self.alt_down:
                    focused_obj = self.window.get_focus()
                    if isinstance(focused_obj, Gtk.IconView):
                        self.is_searching = True
                        wid, tid, self.search_tab, self.search_icon_grid, store = self.get_current_state()
                        self.unset_keys_and_data()
                        self.popup_search_files(wid, keyname)
                        return
