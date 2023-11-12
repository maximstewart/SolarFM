# Python imports

# Lib imports

# Application imports
from .signals.file_action_signals_mixin import FileActionSignalsMixin
from .signals.ipc_signals_mixin import IPCSignalsMixin
from .signals.keyboard_signals_mixin import KeyboardSignalsMixin




class SignalsMixins(FileActionSignalsMixin, KeyboardSignalsMixin, IPCSignalsMixin):
    ...
