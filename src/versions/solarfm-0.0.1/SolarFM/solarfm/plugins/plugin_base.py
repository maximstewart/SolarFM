# Python imports
import os
import time

# Lib imports

# Application imports


class PluginBaseException(Exception):
    ...


class PluginBase:
    def __init__(self):
        self.name               = "Example Plugin"  # NOTE: Need to remove after establishing private bidirectional 1-1 message bus
                                                    #       where self.name should not be needed for message comms

        self._builder           = None
        self._ui_objects        = None
        self._fm_state          = None
        self._event_system      = None


    def set_fm_event_system(self, fm_event_system):
        """
            Requests Key:  'pass_fm_events': "true"
            Must define in plugin if "pass_fm_events" is set to "true" string.
        """
        self._event_system = fm_event_system

    def set_ui_object_collection(self, ui_objects):
        """
            Requests Key:  "pass_ui_objects": [""]
            Request reference to a UI component. Will be passed back as array to plugin.
            Must define in plugin if set and an array of valid glade UI IDs is given.
        """
        self._ui_objects = ui_objects


    def clear_children(self, widget: type) -> None:
        """ Clear children of a gtk widget. """
        for child in widget.get_children():
            widget.remove(child)

    def subscribe_to_events(self):
        self._event_system.subscribe("update_state_info_plugins", self._update_fm_state_info)

    def _update_fm_state_info(self, state):
        self._fm_state = state

    def generate_reference_ui_element(self):
        """
            Requests Key:  'ui_target': "plugin_control_list",
            Must define regardless if needed and can 'pass' if plugin doesn't use it.
            Must return a widget if "ui_target" is set.
        """
        raise PluginBaseException("Method hasn't been overriden...")

    def run(self):
        """
            Must define regardless if needed and can 'pass' if plugin doesn't need it.
            Is intended to be used to setup internal signals or custom Gtk Builders/UI logic.
        """
        raise PluginBaseException("Method hasn't been overriden...")
