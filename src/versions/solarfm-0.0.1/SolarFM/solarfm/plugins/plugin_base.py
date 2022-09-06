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

        self._event_system      = None
        self._event_sleep_time  = .5
        self._event_message     = None

    def set_fm_event_system(self, fm_event_system):
        self._event_system = fm_event_system

    def set_ui_object_collection(self, ui_objects):
        self._ui_objects = ui_objects

    def wait_for_fm_message(self):
        while not self._event_message:
            pass

    def clear_children(self, widget: type) -> None:
        ''' Clear children of a gtk widget. '''
        for child in widget.get_children():
            widget.remove(child)

    @daemon_threaded
    def _module_event_observer(self):
        while True:
            time.sleep(self._event_sleep_time)
            event = self._event_system.read_module_event()
            if event:
                try:
                    if event[0] == self.name:
                        target_id, method_target, data = self._event_system.consume_module_event()

                        if not method_target:
                            self._event_message = data
                        else:
                            method = getattr(self.__class__, f"{method_target}")
                            if data:
                                data = method(*(self, *data))
                            else:
                                method(*(self,))
                except Exception as e:
                    print(repr(e))
