# Python imports

# Lib imports
import inspect
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Application imports




class MessageWidget(Gtk.MessageDialog):
    """docstring for MessageWidget."""

    def __init__(self):
        super(MessageWidget, self).__init__()

        self._setup_styling()
        self._setup_signals()
        self._load_widgets()


    def _setup_styling(self):
        ...

    def _setup_signals(self):
        ...


    def _load_widgets(self):
        ...
