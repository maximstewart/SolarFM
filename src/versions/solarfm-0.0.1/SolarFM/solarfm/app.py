# Python imports
import os, inspect, time

# Lib imports

# Application imports
from utils.settings import Settings
from core.controller import Controller
from __builtins__ import EventSystem




class Application(EventSystem):
    """ Create Settings and Controller classes. Bind signal to Builder. Inherit from Builtins to bind global methods and classes. """

    def __init__(self, args, unknownargs):
        if not trace_debug:
            event_system.create_ipc_listener()
            time.sleep(0.1)

            if not event_system.is_ipc_alive:
                if unknownargs:
                    for arg in unknownargs:
                        if os.path.isdir(arg):
                            message = f"FILE|{arg}"
                            event_system.send_ipc_message(message)

                if args.new_tab and os.path.isdir(args.new_tab):
                    message = f"FILE|{args.new_tab}"
                    event_system.send_ipc_message(message)

                raise Exception("IPC Server Exists: Will send path(s) to it and close...")


        settings = Settings()
        settings.create_window()

        controller = Controller(args, unknownargs, settings)
        if not controller:
            raise Exception("Controller exited and doesn't exist...")

        # Gets the methods from the classes and sets to handler.
        # Then, builder connects to any signals it needs.
        classes  = [controller]
        handlers = {}
        for c in classes:
            methods = None
            try:
                methods = inspect.getmembers(c, predicate=inspect.ismethod)
                handlers.update(methods)
            except Exception as e:
                print(repr(e))

        settings.get_builder().connect_signals(handlers)
