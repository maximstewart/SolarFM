# Python imports
import os, threading, time
from multiprocessing.connection import Listener, Client

# Lib imports

# Application imports




class IPCServer:
    """ Create a listener so that other SolarFM instances send requests back to existing instance. """
    def __init__(self, ipc_address: str = '127.0.0.1', conn_type: str = "socket"):
        self.is_ipc_alive     = False
        self._ipc_port        = 4848
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


    @daemon_threaded
    def create_ipc_listener(self) -> None:
        if self._conn_type == "socket":
            if os.path.exists(self._ipc_address):
                return

            listener = Listener(address=self._ipc_address, family="AF_UNIX", authkey=self._ipc_authkey)
        elif "unsecured" not in self._conn_type:
            listener = Listener((self._ipc_address, self._ipc_port), authkey=self._ipc_authkey)
        else:
            listener = Listener((self._ipc_address, self._ipc_port))


        self.is_ipc_alive = True
        while True:
            conn       = listener.accept()
            start_time = time.perf_counter()
            self.handle_message(conn, start_time)

        listener.close()

    def handle_message(self, conn, start_time) -> None:
        while True:
            msg = conn.recv()
            if debug:
                print(msg)

            if "FILE|" in msg:
                file = msg.split("FILE|")[1].strip()
                if file:
                    event_system.emit("handle_file_from_ipc", file)

                conn.close()
                break


            if msg in ['close connection', 'close server']:
                conn.close()
                break

            # NOTE: Not perfect but insures we don't lock up the connection for too long.
            end_time = time.perf_counter()
            if (end_time - start_time) > self._ipc_timeout:
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
