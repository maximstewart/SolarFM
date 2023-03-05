# Python imports
import os, threading, pickle
from multiprocessing.connection import Listener, Client

# Lib imports
from gi.repository import GLib

# Application imports




class IPCServer:
    """ Create a listener so that other SolarFM instances send requests back to existing instance. """
    def __init__(self, ipc_address: str = '127.0.0.1', conn_type: str = "socket"):
        self.is_ipc_alive     = False
        self._ipc_port        = 4848
        self._ipc_address     = ipc_address
        self._conn_type       = conn_type
        self._ipc_authkey     = b'' + bytes(f'solarfm-search_grep-ipc', 'utf-8')
        self._ipc_timeout     = 15.0

        if conn_type == "socket":
            self._ipc_address = f'/tmp/solarfm-search_grep-ipc.sock'
        elif conn_type == "full_network":
            self._ipc_address = '0.0.0.0'
        elif conn_type == "full_network_unsecured":
            self._ipc_authkey = None
            self._ipc_address = '0.0.0.0'
        elif conn_type == "local_network_unsecured":
            self._ipc_authkey = None


    @daemon_threaded
    def create_ipc_listener(self) -> None:
        if self._conn_type == "socket":
            if os.path.exists(self._ipc_address):
                os.unlink(self._ipc_address)

            listener = Listener(address=self._ipc_address, family="AF_UNIX", authkey=self._ipc_authkey)
        elif "unsecured" not in self._conn_type:
            listener = Listener((self._ipc_address, self._ipc_port), authkey=self._ipc_authkey)
        else:
            listener = Listener((self._ipc_address, self._ipc_port))


        self.is_ipc_alive = True
        while True:
            conn = listener.accept()

            if not self.pause_fifo_update:
                self.handle_message(conn)
            else:
                conn.close()

        listener.close()

    def handle_message(self, conn) -> None:
        while True:
            msg  = conn.recv()

            try:
                if "SEARCH_DONE|" in msg:
                    ts, ret_code = msg.split("SEARCH_DONE|")[1].strip().split("|", 1)
                    timestamp = float(ts)
                    if self.fsearch_time_stamp or self.grep_time_stamp:
                        if (timestamp > self.fsearch_time_stamp) or (timestamp > self.grep_time_stamp):
                            GLib.idle_add(self.stop_spinner, (ret_code,), priority=GLib.PRIORITY_HIGH_IDLE)

                if "SEARCH|" in msg:
                    ts, file = msg.split("SEARCH|")[1].strip().split("|", 1)
                    timestamp = float(ts)
                    if file and (timestamp > self.fsearch_time_stamp):
                        GLib.idle_add(self._load_file_ui, file, priority=GLib.PRIORITY_HIGH_IDLE)

                if "GREP|" in msg:
                    ts, data = msg.split("GREP|")[1].strip().split("|", 1)
                    timestamp = float(ts)
                    if data and (timestamp > self.grep_time_stamp):
                        GLib.idle_add(self._load_grep_ui, data, priority=GLib.PRIORITY_HIGH_IDLE)
            except Exception as e:
                print( repr(e) )


            conn.close()
            break

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
            print("Connection refused...")
        except Exception as e:
            print(repr(e))
