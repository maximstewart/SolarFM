# Python imports
import os, threading, time
from multiprocessing.connection import Listener, Client

# Lib imports

# Application imports


def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs, daemon=True).start()
    return wrapper




class IPCServer:
    """ Create a listener so that other SolarFM instances send requests back to existing instance. """
    def __init__(self, conn_type: str = "socket"):
        self.is_ipc_alive   = False
        self._conn_type     = conn_type
        self.ipc_authkey    = b'solarfm-ipc'
        self.ipc_timeout    = 15.0

        if conn_type == "socket":
            self.ipc_address    = '/tmp/solarfm-ipc.sock'
        else:
            self.ipc_address    = '127.0.0.1'
            self.ipc_port       = 4848


    @threaded
    def create_ipc_server(self) -> None:
        if self._conn_type == "socket":
            if os.path.exists(self.ipc_address):
                return

            listener = Listener(address=self.ipc_address, family="AF_UNIX", authkey=self.ipc_authkey)
        else:
            listener = Listener((self.ipc_address, self.ipc_port), authkey=self.ipc_authkey)


        self.is_ipc_alive = True
        while True:
            conn       = listener.accept()
            start_time = time.perf_counter()

            print(f"New Connection: {listener.last_accepted}")
            while True:
                msg = conn.recv()
                if debug:
                    print(msg)

                if "FILE|" in msg:
                    file = msg.split("FILE|")[1].strip()
                    if file:
                        event_system.push_gui_event([None, "handle_file_from_ipc", (file,)])

                    conn.close()
                    break


                if msg == 'close connection':
                    conn.close()
                    break
                if msg == 'close server':
                    conn.close()
                    break

                # NOTE: Not perfect but insures we don't lock up the connection for too long.
                end_time = time.perf_counter()
                if (end - start) > self.ipc_timeout:
                    conn.close()

        listener.close()


    def send_ipc_message(self, message: str = "Empty Data...") -> None:
        try:
            if self._conn_type == "socket":
                conn = Client(address=self.ipc_address, family="AF_UNIX", authkey=self.ipc_authkey)
            else:
                conn = Client((self.ipc_address, self.ipc_port), authkey=self.ipc_authkey)


            conn.send(message)
            conn.send('close connection')
            conn.close()
        except Exception as e:
            print(repr(e))
