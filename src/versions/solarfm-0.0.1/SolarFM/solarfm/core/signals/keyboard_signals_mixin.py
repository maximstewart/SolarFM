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

    # TODO: Need to set methods that use this to somehow check the keybindings state instead.
    def unset_keys_and_data(self, widget=None, eve=None):
        self.ctrl_down    = False
        self.shift_down   = False
        self.alt_down     = False
        self.is_searching = False

    def on_global_key_press_controller(self, eve, user_data):
        keyname = Gdk.keyval_name(user_data.keyval).lower()
        if keyname.replace("_l", "").replace("_r", "") in ["control", "alt", "shift"]:
            if "control" in keyname:
                self.ctrl_down    = True
            if "shift" in keyname:
                self.shift_down   = True
            if "alt" in keyname:
                self.alt_down     = True

    def on_global_key_release_controller(self, widget, event):
        """Handler for keyboard events"""
        keyname = Gdk.keyval_name(event.keyval).lower()
        if keyname.replace("_l", "").replace("_r", "") in ["control", "alt", "shift"]:
            if "control" in keyname:
                self.ctrl_down    = False
            if "shift" in keyname:
                self.shift_down   = False
            if "alt" in keyname:
                self.alt_down     = False

        mapping = self.keybindings.lookup(event)
        if mapping:
            try:
                # See if in filemanager scope
                getattr(self, mapping)()
                return True
            except Exception:
                # Must be plugins scope or we forgot to add method to file manager scope
                sender, method_target = mapping.split("||")
                self.handle_plugin_key_event(sender, method_target)
        else:
            if debug:
                print(f"on_global_key_release_controller > key > {keyname}")

            if self.ctrl_down:
                if keyname in ["1", "kp_1", "2", "kp_2", "3", "kp_3", "4", "kp_4"]:
                    self.builder.get_object(f"tggl_notebook_{keyname.strip('kp_')}").released()

            if re.fullmatch(valid_keyvalue_pat, keyname):
                if not self.is_searching and not self.ctrl_down \
                    and not self.shift_down and not self.alt_down:
                        focused_obj = self.window.get_focus()
                        if isinstance(focused_obj, Gtk.IconView):
                            self.is_searching     = True
                            state                 = self.get_current_state()
                            self.search_tab       = state.tab
                            self.search_icon_grid = state.icon_grid

                            self.unset_keys_and_data()
                            self.popup_search_files(state.wid, keyname)
                            return True


    def keyboard_close_tab(self):
        wid, tid  = self.fm_controller.get_active_wid_and_tid()
        notebook  = self.builder.get_object(f"window_{wid}")
        scroll    = self.builder.get_object(f"{wid}|{tid}")
        page      = notebook.page_num(scroll)
        tab       = self.get_fm_window(wid).get_tab_by_id(tid)
        watcher   = tab.get_dir_watcher()
        watcher.cancel()

        self.get_fm_window(wid).delete_tab_by_id(tid)
        notebook.remove_page(page)
        self.fm_controller.save_state()
        self.set_window_title()
