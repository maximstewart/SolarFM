# Python imports
import re

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk

# Application imports



valid_keyvalue_pat = re.compile(r"[a-z0-9A-Z-_\[\]\(\)\| ]")



class KeyboardSignalsMixin:
    """ KeyboardSignalsMixin keyboard hooks controller. """

    # TODO: Need to set methods that use this to somehow check the keybindings state instead.
    def unset_keys_and_data(self, widget = None, eve = None):
        self.ctrl_down    = False
        self.shift_down   = False
        self.alt_down     = False

    def unmap_special_keys(self, keyname):
        if "control" in keyname:
            self.ctrl_down    = False
        if "shift" in keyname:
            self.shift_down   = False
        if "alt" in keyname:
            self.alt_down     = False

    def on_global_key_press_controller(self, eve, user_data):
        keyname = Gdk.keyval_name(user_data.keyval).lower()
        modifiers = Gdk.ModifierType(user_data.get_state() & ~Gdk.ModifierType.LOCK_MASK)

        self.was_midified_key = True if modifiers != 0 else False

        if keyname.replace("_l", "").replace("_r", "") in ["control", "alt", "shift"]:
            if "control" in keyname:
                self.ctrl_down    = True
            if "shift" in keyname:
                self.shift_down   = True
            if "alt" in keyname:
                self.alt_down     = True

    def on_global_key_release_controller(self, widget, event):
        """ Handler for keyboard events """
        keyname   = Gdk.keyval_name(event.keyval).lower()
        modifiers = Gdk.ModifierType(event.get_state() & ~Gdk.ModifierType.LOCK_MASK)

        if keyname.replace("_l", "").replace("_r", "") in ["control", "alt", "shift"]:
            should_return = self.was_midified_key and (self.ctrl_down or self.shift_down or self.alt_down)
            self.unmap_special_keys(keyname)

            if should_return:
                self.was_midified_key = False
                return

        mapping = keybindings.lookup(event)
        logger.debug(f"on_global_key_release_controller > key > {keyname}")
        logger.debug(f"on_global_key_release_controller > keyval > {event.keyval}")
        logger.debug(f"on_global_key_release_controller > mapping > {mapping}")

        if mapping:
            self.handle_mapped_key_event(mapping)
        else:
            self.handle_as_key_event_scope(keyname)

    def handle_mapped_key_event(self, mapping):
        try:
            self.handle_as_controller_scope(mapping)
        except Exception:
            self.handle_as_plugin_scope(mapping)

    def handle_as_controller_scope(self, mapping):
        getattr(self, mapping)()

    def handle_as_plugin_scope(self, mapping):
        if "||" in mapping:
            sender, eve_type = mapping.split("||")
        else:
            sender = ""
            eve_type = mapping

        self.handle_key_event_system(sender, eve_type)

    def handle_as_key_event_scope(self, keyname):
        if self.ctrl_down and not keyname in ["1", "kp_1", "2", "kp_2", "3", "kp_3", "4", "kp_4"]:
            self.handle_key_event_system(None, keyname)

    def handle_key_event_system(self, sender, eve_type):
        event_system.emit(eve_type)