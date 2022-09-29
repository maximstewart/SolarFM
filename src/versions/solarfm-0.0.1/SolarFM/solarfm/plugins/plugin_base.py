# Python imports
import os, time

# Lib imports

# Application imports


class PluginBase:
    def __init__(self):
        self.name               = "Example Plugin"  # NOTE: Need to remove after establishing private bidirectional 1-1 message bus
                                                    #       where self.name should not be needed for message comms

        self._builder           = None
        self._ui_objects        = None
        self._fm_state          = None
        self._event_system      = None


    def set_fm_event_system(self, fm_event_system):
        self._event_system = fm_event_system

    def set_ui_object_collection(self, ui_objects):
        self._ui_objects = ui_objects


    def clear_children(self, widget: type) -> None:
        ''' Clear children of a gtk widget. '''
        for child in widget.get_children():
            widget.remove(child)

    def subscribe_to_events(self):
        self._event_system.subscribe("update_state_info_plugins", self._update_fm_state_info)

    def _update_fm_state_info(self, state):
        self._fm_state = state
