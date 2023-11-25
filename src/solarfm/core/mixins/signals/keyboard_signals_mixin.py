# Python imports
import re

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk

# Application imports


valid_keyvalue_pat    = re.compile(r"[a-z0-9A-Z-_\[\]\(\)\| ]")




class KeyboardSignalsMixin:
    """ KeyboardSignalsMixin keyboard hooks controller. """

    # TODO: Need to set methods that use this to somehow check the keybindings state instead.
    def unset_keys_and_data(self, widget=None, eve=None):
        self.ctrl_down    = False
        self.shift_down   = False
        self.alt_down     = False

    def unmap_special_key(self, keyname):
        if "control" in keyname:
            self.ctrl_down    = False
        if "shift" in keyname:
            self.shift_down   = False
        if "alt" in keyname:
            self.alt_down     = False

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
            self.unmap_special_key(keyname)

        mapping = keybindings.lookup(event)
        if mapping:
            try:
                self.handle_as_controller_scope(mapping)
            except Exception:
                self.handle_as_plugin_scope(mapping)
        else:
            logger.debug(f"on_global_key_release_controller > key > {keyname}")

            if self.ctrl_down:
                if keyname in ["1", "kp_1", "2", "kp_2", "3", "kp_3", "4", "kp_4"]:
                    self.builder.get_object(f"tggl_notebook_{keyname.strip('kp_')}").released()

    def handle_as_controller_scope(self, mapping):
        getattr(self, mapping)()

    def handle_as_plugin_scope(self, mapping):
        if "||" in mapping:
            sender, eve_type = mapping.split("||")
        else:
            sender = ""
            eve_type = mapping

        self.handle_as_key_event_system(sender, eve_type)

    def handle_as_key_event_system(self, sender, eve_type):
        event_system.emit(eve_type)

    def keyboard_close_tab(self):
        wid, tid  = self.fm_controller.get_active_wid_and_tid()
        notebook  = self.builder.get_object(f"window_{wid}")
        scroll    = self.builder.get_object(f"{wid}|{tid}", use_gtk = False)
        page      = notebook.page_num(scroll)
        tab       = self.get_fm_window(wid).get_tab_by_id(tid)
        watcher   = tab.get_dir_watcher()
        watcher.cancel()

        self.get_fm_window(wid).delete_tab_by_id(tid)
        notebook.remove_page(page)
        if not settings_manager.is_trace_debug():
            self.fm_controller.save_state()
        self.set_window_title()