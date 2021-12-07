# Python imports
import threading, socket, time
from multiprocessing.connection import Listener, Client

# Lib imports

# Application imports


def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()
    return wrapper




class DBusControllerMixin:

    @threaded
    def create_ipc_server(self):
        listener          = Listener(('127.0.0.1', 4848), authkey=b'solarfm-ipc')
        self.is_ipc_alive = True
        while event_system.keep_ipc_alive:
            conn       = listener.accept()
            start_time = time.time()

            print(f"New Connection: {listener.last_accepted}")
            while True:
                msg = conn.recv()
                if debug:
                    print(msg)

                if "FILE|" in msg:
                    file = msg.split("FILE|")[1].strip()
                    if file:
                        event_system.push_gui_event(["create_tab_from_ipc", None, file])

                    conn.close()
                    break


                if msg == 'close connection':
                    conn.close()
                    break
                if msg == 'close server':
                    conn.close()
                    event_system.keep_ipc_alive = False
                    break

                # NOTE: Not perfect but insures we don't lockup the connection for too long.
                end_time = time.time()
                if (end - start) > 15.0:
                    conn.close()

        listener.close()


    def send_ipc_message(self, message="Empty Data..."):
        try:
            conn = Client(('127.0.0.1', 4848), authkey=b'solarfm-ipc')
            conn.send(message)
            conn.send('close connection')
        except Exception as e:
            print(repr(e))
