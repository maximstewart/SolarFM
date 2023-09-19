# Python imports
import builtins
import threading
import sys

# Lib imports

# Application imports
from utils.event_system import EventSystem
from utils.endpoint_registry import EndpointRegistry
from utils.keybindings import Keybindings
from utils.logger import Logger
from utils.settings_manager.manager import SettingsManager


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

def sizeof_fmt_def(num, suffix="B"):
    for unit in ["", "K", "M", "G", "T", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f} {unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f} Yi{suffix}"



# NOTE: Just reminding myself we can add to builtins two different ways...
# __builtins__.update({"event_system": Builtins()})
builtins.app_name          = "SolarFM"
builtins.keybindings       = Keybindings()
builtins.event_system      = EventSystem()
builtins.endpoint_registry = EndpointRegistry()
builtins.settings_manager  = SettingsManager()

settings_manager.load_settings()

builtins.settings          = settings_manager.settings
builtins.logger            = Logger(settings_manager.get_home_config_path(), \
                                    _ch_log_lvl=settings.debugging.ch_log_lvl, \
                                    _fh_log_lvl=settings.debugging.fh_log_lvl).get_logger()

builtins.threaded          = threaded_wrapper
builtins.daemon_threaded   = daemon_threaded_wrapper
builtins.sizeof_fmt        = sizeof_fmt_def
builtins.event_sleep_time  = 0.05


def custom_except_hook(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = custom_except_hook
