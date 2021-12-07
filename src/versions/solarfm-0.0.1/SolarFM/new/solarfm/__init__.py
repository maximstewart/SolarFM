# Python imports
import os, inspect, time

# Gtk imports

# Application imports
from utils import Settings
from signal_classes import Controller
from __builtins__ import Builtins


class Main(Builtins):
    def __init__(self, args, unknownargs):
        event_system.create_ipc_server()
        time.sleep(0.5)
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
        settings.createWindow()

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

        settings.builder.connect_signals(handlers)
