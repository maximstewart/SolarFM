# Python imports
import builtins, threading

# Lib imports

# Application imports
from utils.event_system import EventSystem




# NOTE: Threads WILL NOT die with parent's destruction.
def threaded_wrapper(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs, daemon=False).start()
    return wrapper

# NOTE: Threads WILL die with parent's destruction.
def daemon_threaded_wrapper(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs, daemon=True).start()
    return wrapper




class EndpointRegistry():
    def __init__(self):
        self._endpoints = {}

    def register(self, rule, **options):
        def decorator(f):
            self._endpoints[rule] = f
            return f

        return decorator

    def get_endpoints(self):
        return self._endpoints




# NOTE: Just reminding myself we can add to builtins two different ways...
# __builtins__.update({"event_system": Builtins()})
builtins.app_name          = "SolarFM"
builtins.event_system      = EventSystem()
builtins.endpoint_registry = EndpointRegistry()
builtins.threaded          = threaded_wrapper
builtins.daemon_threaded   = daemon_threaded_wrapper
builtins.event_sleep_time  = 0.05
builtins.trace_debug       = False
builtins.debug             = False
builtins.app_settings      = None
