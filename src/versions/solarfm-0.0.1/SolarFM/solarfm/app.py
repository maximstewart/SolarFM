# Python imports
import os, inspect

# Lib imports

# Application imports

from utils.ipc_server import IPCServer
from core.controller import Controller


class AppLaunchException(Exception):
    ...

class ControllerStartException(Exception):
    ...


class Application(IPCServer):
    """ Inherit from IPCServer; create Controller classe; bind any signal(s) to Builder. """

    def __init__(self, args, unknownargs):
        super(Application, self).__init__()
        self.args, self.unknownargs = args, unknownargs

        if not settings.is_trace_debug():
            try:
                self.create_ipc_listener()
            except Exception:
                ...

            if not self.is_ipc_alive:
                for arg in unknownargs + [args.new_tab,]:
                    if os.path.isdir(arg):
                        message = f"FILE|{arg}"
                        self.send_ipc_message(message)

                raise AppLaunchException(f"{app_name} IPC Server Exists: Will send path(s) to it and close...")


        settings.create_window()
        self._load_controller_and_builder()

    def _load_controller_and_builder(self):
        controller = Controller(self.args, self.unknownargs)
        if not controller:
            raise ControllerStartException("Controller exited and doesn't exist...")

        # Gets the methods from the classes and sets to handler.
        # Then, builder connects to any signals it needs.
        classes  = [controller]
        handlers = {}
        for c in classes:
            methods = None
            try:
                methods = inspect.getmembers(c, predicate=inspect.ismethod)
                handlers.update(methods)
            except AppLaunchException as e:
                print(repr(e))

        settings.get_builder().connect_signals(handlers)
