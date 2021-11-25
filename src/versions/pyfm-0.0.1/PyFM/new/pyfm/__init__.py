# Python imports
import inspect, time

# Gtk imports

# Application imports
from utils import Settings
from signal_classes import Signals
from __builtins__ import Builtins


class Main(Builtins):
    def __init__(self, args):
        event_system.create_ipc_server()
        time.sleep(0.5)
        if not event_system.is_ipc_alive:
            if args.new_tab:
                message = f"FILE|{args.new_tab}"
                event_system.send_ipc_message(message)
            raise Exception("IPC Server Exists: Will send message to it and close...")

        settings = Settings()
        settings.createWindow()

        signals = Signals(args, settings)
        if not signals:
            raise Exception("Signals exited...")

        # Gets the methods from the classes and sets to handler.
        # Then, builder connects to any signals it needs.
        classes  = [signals]
        handlers = {}
        for c in classes:
            methods = None
            try:
                methods = inspect.getmembers(c, predicate=inspect.ismethod)
                handlers.update(methods)
            except Exception as e:
                pass

        settings.builder.connect_signals(handlers)
        window = settings.createWindow()
