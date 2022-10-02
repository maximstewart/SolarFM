# Python imports
import os, inspect, time

# Lib imports

# Application imports
from __builtins__ import *
from utils.ipc_server import IPCServer
from utils.settings import Settings
from core.controller import Controller


class AppLaunchException(Exception):
    ...

class ControllerStartExceptio(Exception):
    ...


class Application(IPCServer):
    """ Create Settings and Controller classes. Bind signal to Builder. Inherit from Builtins to bind global methods and classes. """

    def __init__(self, args, unknownargs):
        super(Application, self).__init__()

        if not trace_debug:
            self.create_ipc_listener()
            time.sleep(0.05)

            if not self.is_ipc_alive:
                if unknownargs:
                    for arg in unknownargs:
                        if os.path.isdir(arg):
                            message = f"FILE|{arg}"
                            self.send_ipc_message(message)

                if args.new_tab and os.path.isdir(args.new_tab):
                    message = f"FILE|{args.new_tab}"
                    self.send_ipc_message(message)

                raise AppLaunchException(f"IPC Server Exists: Will send path(s) to it and close...\nNote: If no fm exists, remove /tmp/{app_name}-ipc.sock")


        settings = Settings()
        settings.create_window()

        controller = Controller(args, unknownargs, settings)
        if not controller:
            raise ControllerStartExceptio("Controller exited and doesn't exist...")

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
