# Python imports
import os
import time
from multiprocessing.connection import Client
from multiprocessing.connection import Listener

# Lib imports
from gi.repository import GLib

# Application imports
from .singleton import Singleton



class IPCServer(Singleton):
    """ Create a listener so that other SolarFM instances send requests back to existing instance. """
    def __init__(self, ipc_address: str = '127.0.0.1', conn_type: str = "local_network_unsecured"):
        self.is_ipc_alive     = False
        self._ipc_port        = 0 # Use 0 to let Listener chose port
        self._ipc_address     = ipc_address
        self._conn_type       = conn_type
        self._ipc_authkey     = b'' + bytes(f'{app_name}-ipc', 'utf-8')
        self._ipc_timeout     = 15.0

        if conn_type == "socket":
            self._ipc_address = f'/tmp/{app_name}-ipc.sock'
        elif conn_type == "full_network":
            self._ipc_address = '0.0.0.0'
        elif conn_type == "full_network_unsecured":
            self._ipc_authkey = None
            self._ipc_address = '0.0.0.0'
        elif conn_type == "local_network_unsecured":
            self._ipc_authkey = None

        self._subscribe_to_events()


    def _subscribe_to_events(self):
        event_system.subscribe("post_file_to_ipc", self.send_ipc_message)

    def create_ipc_listener(self) -> None:
        if self._conn_type == "socket":
            if os.path.exists(self._ipc_address) and settings_manager.is_dirty_start():
                os.unlink(self._ipc_address)

            listener = Listener(address = self._ipc_address, family = "AF_UNIX", authkey = self._ipc_authkey)

        elif "unsecured" not in self._conn_type:
            listener = Listener((self._ipc_address, self._ipc_port), authkey = self._ipc_authkey)
        else:
            listener = Listener((self._ipc_address, self._ipc_port))

        self.is_ipc_alive = True
        # self._run_ipc_loop(listener)
        GLib.Thread("", self._run_ipc_loop, listener)

    # @daemon_threaded
    def _run_ipc_loop(self, listener) -> None:
        while True:
            try:
                conn       = listener.accept()
                start_time = time.perf_counter()

                GLib.idle_add(self._handle_ipc_message, *(conn, start_time,))

                conn       = None
                start_time = None
            except Exception as e:
                logger.debug( repr(e) )

        listener.close()

    def _handle_ipc_message(self, conn, start_time) -> None:
        while True:
            msg = conn.recv()
            logger.debug(msg)

            if "FILE|" in msg:
                file = msg.split("FILE|")[1].strip()
                if file:
                    event_system.emit_and_await("handle_file_from_ipc", file)

                msg  = None
                file = None
                conn.close()
                break


            if msg in ['close connection', 'close server']:
                msg  = None
                conn.close()
                break

            # NOTE: Not perfect but insures we don't lock up the connection for too long.
            end_time = time.perf_counter()
            if (end_time - start_time) > self._ipc_timeout:
                msg      = None
                end_time = None
                conn.close()
                break

        return False


    def send_ipc_message(self, message: str = "Empty Data...") -> None:
        try:
            if self._conn_type == "socket":
                conn = Client(address=self._ipc_address, family="AF_UNIX", authkey=self._ipc_authkey)
            elif "unsecured" not in self._conn_type:
                conn = Client((self._ipc_address, self._ipc_port), authkey=self._ipc_authkey)
            else:
                conn = Client((self._ipc_address, self._ipc_port))

            conn.send(message)
            conn.close()
        except ConnectionRefusedError as e:
            logger.error("Connection refused...")
        except Exception as e:
            logger.error( repr(e) )


    def send_test_ipc_message(self, message: str = "Empty Data...") -> None:
        try:
            if self._conn_type == "socket":
                conn = Client(address=self._ipc_address, family="AF_UNIX", authkey=self._ipc_authkey)
            elif "unsecured" not in self._conn_type:
                conn = Client((self._ipc_address, self._ipc_port), authkey=self._ipc_authkey)
            else:
                conn = Client((self._ipc_address, self._ipc_port))

            conn.send(message)
            conn.close()
        except ConnectionRefusedError as e:
            if self._conn_type == "socket":
                logger.error("IPC Socket no longer valid.... Removing.")
                os.unlink(self._ipc_address)
        except Exception as e:
            logger.error( repr(e) )
