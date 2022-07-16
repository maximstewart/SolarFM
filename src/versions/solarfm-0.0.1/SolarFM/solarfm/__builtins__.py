# Python imports
import builtins

# Lib imports

# Application imports
from utils.ipc_server import IPCServer




class EventSystem(IPCServer):
    """ Inheret IPCServerMixin. Create an pub/sub systems. """

    def __init__(self):
        super(EventSystem, self).__init__()

        # NOTE: The format used is list of ['who', target, (data,)] Where:
        #             who is the sender or target ID and is used for context and control flow,
        #             method_target is the method to call,
        #             data is the method parameters OR message data to give
        #       Where data may be any kind of data
        self._gui_events    = []
        self._module_events = []



    # Makeshift "events" system FIFO
    def _pop_gui_event(self) -> None:
        if len(self._gui_events) > 0:
            return self._gui_events.pop(0)
        return None

    def _pop_module_event(self) -> None:
        if len(self._module_events) > 0:
            return self._module_events.pop(0)
        return None


    def push_gui_event(self, event: list) -> None:
        if len(event) == 3:
            self._gui_events.append(event)
            return None

        raise Exception("Invald event format! Please do:  ['sender_id': str, method_target: method, (data,): any]")

    def push_module_event(self, event: list) -> None:
        if len(event) == 3:
            self._module_events.append(event)
            return None

        raise Exception("Invald event format! Please do:  ['target_id': str, method_target: method, (data,): any]")

    def read_gui_event(self) -> list:
        return self._gui_events[0] if self._gui_events else None

    def read_module_event(self) -> list:
        return self._module_events[0] if self._module_events else None

    def consume_gui_event(self) -> list:
        return self._pop_gui_event()

    def consume_module_event(self) -> list:
        return self._pop_module_event()



# NOTE: Just reminding myself we can add to builtins two different ways...
# __builtins__.update({"event_system": Builtins()})
builtins.app_name          = "SolarFM"
builtins.event_system      = EventSystem()
builtins.event_sleep_time  = 0.05
builtins.trace_debug       = False
builtins.debug             = False
