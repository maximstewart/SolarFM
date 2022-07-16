# Python imports
import threading, json
from os import path

# Lib imports

# Application imports
from .window import Window


def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs, daemon=True).start()
    return wrapper


class WindowController:
    def __init__(self):
        USER_HOME               = path.expanduser('~')
        CONFIG_PATH             = USER_HOME   + "/.config/solarfm"
        self._session_file      = CONFIG_PATH + "/session.json"

        self._event_sleep_time  = 1
        self._active_window_id  = ""
        self._active_tab_id     = ""
        self._windows           = []


    def set_wid_and_tid(self, wid, tid):
        self._active_window_id = str(wid)
        self._active_tab_id    = str(tid)

    def get_active_wid_and_tid(self):
        return self._active_window_id, self._active_tab_id

    def create_window(self):
        window = Window()
        window.set_nickname(f"window_{str(len(self._windows) + 1)}")
        self._windows.append(window)
        return window


    def add_tab_for_window(self, win_id):
        for window in self._windows:
            if window.get_id() == win_id:
                return window.create_tab()

    def add_tab_for_window_by_name(self, name):
        for window in self._windows:
            if window.get_name() == name:
                return window.create_tab()

    def add_tab_for_window_by_nickname(self, nickname):
        for window in self._windows:
            if window.get_nickname() == nickname:
                return window.create_tab()

    def pop_window(self):
        self._windows.pop()

    def delete_window_by_id(self, win_id):
        for window in self._windows:
            if window.get_id() == win_id:
                self._windows.remove(window)
                break

    def delete_window_by_name(self, name):
        for window in self._windows:
            if window.get_name() == name:
                self._windows.remove(window)
                break

    def delete_window_by_nickname(self, nickname):
        for window in self._windows:
            if window.get_nickname() == nickname:
                self._windows.remove(window)
                break

    def get_window_by_id(self, win_id):
        for window in self._windows:
            if window.get_id() == win_id:
                return window

        raise(f"No Window by ID {win_id} found!")

    def get_window_by_name(self, name):
        for window in self._windows:
            if window.get_name() == name:
                return window

        raise(f"No Window by Name {name} found!")

    def get_window_by_nickname(self, nickname):
        for window in self._windows:
            if window.get_nickname() == nickname:
                return window

        raise(f"No Window by Nickname {nickname} found!")

    def get_window_by_index(self, index):
        return self._windows[index]

    def get_all_windows(self):
        return self._windows


    def set_window_nickname(self, win_id = None, nickname = ""):
        for window in self._windows:
            if window.get_id() == win_id:
                window.set_nickname(nickname)

    def list_windows(self):
        print("\n[  ----  Windows  ----  ]\n")
        for window in self._windows:
            print(f"\nID: {window.get_id()}")
            print(f"Name: {window.get_name()}")
            print(f"Nickname: {window.get_nickname()}")
            print(f"Is Hidden: {window.is_hidden()}")
            print(f"Tab Count: {window.get_tabs_count()}")
        print("\n-------------------------\n")



    def list_files_from_tabs_of_window(self, win_id):
        for window in self._windows:
            if window.get_id() == win_id:
                window.list_files_from_tabs()
                break

    def get_tabs_count(self, win_id):
        for window in self._windows:
            if window.get_id() == win_id:
                return window.get_tabs_count()

    def get_tabs_from_window(self, win_id):
        for window in self._windows:
            if window.get_id() == win_id:
                return window.get_all_tabs()




    def unload_tabs_and_windows(self):
        for window in self._windows:
            window.get_all_tabs().clear()

        self._windows.clear()

    def save_state(self, session_file = None):
        if not session_file:
            session_file = self._session_file

        if len(self._windows) > 0:
            windows = []
            for window in self._windows:
                tabs = []
                for tab in window.get_all_tabs():
                    tabs.append(tab.get_current_directory())

                windows.append(
                    [
                        {
                            'window':{
                                "ID": window.get_id(),
                                "Name": window.get_name(),
                                "Nickname": window.get_nickname(),
                                "isHidden": f"{window.is_hidden()}",
                                'tabs': tabs
                            }
                        }
                    ]
                )

            with open(session_file, 'w') as outfile:
                json.dump(windows, outfile, separators=(',', ':'), indent=4)
        else:
            raise Exception("Window data corrupted! Can not save session!")

    def get_state_from_file(self, session_file = None):
        if not session_file:
            session_file = self._session_file

        if path.isfile(session_file):
            with open(session_file) as infile:
                return json.load(infile)
