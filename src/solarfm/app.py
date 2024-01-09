# Python imports
import signal
import os

# Lib imports

# Application imports
from utils.debugging import debug_signal_handler
from utils.ipc_server import IPCServer
from core.window import Window



class AppLaunchException(Exception):
    ...



class Application:
    """ docstring for Application. """

    def __init__(self, args, unknownargs):
        super(Application, self).__init__()

        if not settings_manager.is_trace_debug():
            self.load_ipc(args, unknownargs)

        self.setup_debug_hook()
        Window(args, unknownargs).main()


    def load_ipc(self, args, unknownargs):
        ipc_server = IPCServer()
        self.ipc_realization_check(ipc_server)

        if not ipc_server.is_ipc_alive:
            for arg in unknownargs + [args.new_tab,]:
                if os.path.isfile(arg):
                    message = f"FILE|{arg}"
                    ipc_server.send_ipc_message(message)

            raise AppLaunchException(f"{app_name} IPC Server Exists: Have sent path(s) to it and closing...")

    def ipc_realization_check(self, ipc_server):
        try:
            ipc_server.create_ipc_listener()
        except Exception:
            ipc_server.send_test_ipc_message()

        try:
            ipc_server.create_ipc_listener()
        except Exception as e:
            ...

    def setup_debug_hook(self):
        try:
            # kill -SIGUSR2 <pid> from Linux/Unix or SIGBREAK signal from Windows
            signal.signal(
                vars(signal).get("SIGBREAK") or vars(signal).get("SIGUSR1"),
                debug_signal_handler
            )
        except ValueError:
            # Typically: ValueError: signal only works in main thread
            ...