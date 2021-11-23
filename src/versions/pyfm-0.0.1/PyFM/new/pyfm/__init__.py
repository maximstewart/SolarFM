# Python imports
import inspect


# Gtk imports


# Application imports
from utils import Settings
from signal_classes import Signals
from __builtins__ import Builtins


class Main(Builtins):
    def __init__(self, args):
        settings = Settings()
        settings.createWindow()

        # Gets the methods from the classes and sets to handler.
        # Then, builder connects to any signals it needs.
        classes  = [Signals(settings)]

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
