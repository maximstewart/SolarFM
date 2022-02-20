# Python imports
import builtins

# Lib imports

# Application imports
from context.ipc_server_mixin import IPCServerMixin




class Builtins(IPCServerMixin):
    """ Inheret IPCServerMixin. Create an pub/sub systems. """

    def __init__(self):
        # NOTE: The format used is list of [type, target, (data,)] Where:
        #             type is useful context for control flow,
        #             target is the method to call,
        #             data is the method parameters to give
        #       Where data may be any kind of data
        self._gui_events    = []
        self._module_events = []
        self.is_ipc_alive   = False
        self.ipc_authkey    = b'solarfm-ipc'
        self.ipc_address    = '127.0.0.1'
        self.ipc_port       = 4848
        self.ipc_timeout    = 15.0


    # Makeshift fake "events" type system FIFO
    def _pop_gui_event(self):
        if len(self._gui_events) > 0:
            return self._gui_events.pop(0)
        return None

    def _pop_module_event(self):
        if len(self._module_events) > 0:
            return self._module_events.pop(0)
        return None


    def push_gui_event(self, event):
        if len(event) == 3:
            self._gui_events.append(event)
            return None

        raise Exception("Invald event format! Please do:  [type, target, (data,)]")

    def push_module_event(self, event):
        if len(event) == 3:
            self._module_events.append(event)
            return None

        raise Exception("Invald event format! Please do:  [type, target, (data,)]")

    def read_gui_event(self):
        return self._gui_events[0]

    def read_module_event(self):
        return self._module_events[0]

    def consume_gui_event(self):
        return self._pop_gui_event()

    def consume_module_event(self):
        return self._pop_module_event()



# NOTE: Just reminding myself we can add to builtins two different ways...
# __builtins__.update({"event_system": Builtins()})
builtins.app_name          = "SolarFM"
builtins.event_system      = Builtins()
builtins.event_sleep_time  = 0.2
builtins.debug             = False
builtins.trace_debug       = False
