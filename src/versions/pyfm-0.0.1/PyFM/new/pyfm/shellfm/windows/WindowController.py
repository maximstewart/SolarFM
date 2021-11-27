# Python imports
import threading, subprocess, time, json
from os import path

# Lib imports

# Application imports
from . import Window


def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()
    return wrapper


class WindowController:
    def __init__(self):
        USER_HOME              = path.expanduser('~')
        CONFIG_PATH            = USER_HOME   + "/.config/pyfm"
        self.session_file      = CONFIG_PATH + "/session.json"

        self._event_sleep_time = 1
        self.active_window_id  = ""
        self.active_tab_id     = ""
        self.windows           = []
        self.fm_event_observer()

    @threaded
    def fm_event_observer(self):
        while event_system.monitor_events:
            time.sleep(event_sleep_time)
            event = event_system.consume_fm_event()
            if event:
                print(event)

    def set_active_data(self, wid, tid):
        self.active_window_id = str(wid)
        self.active_tab_id    = str(tid)

    def get_active_data(self):
        return self.active_window_id, self.active_tab_id

    def create_window(self):
        window          = Window()
        window.name     = "window_" + window.id
        window.nickname = "window_" + str(len(self.windows) + 1)

        self.windows.append(window)
        return window


    def add_view_for_window(self, win_id):
        for window in self.windows:
            if window.id == win_id:
                return window.create_view()

    def add_view_for_window_by_name(self, name):
        for window in self.windows:
            if window.name == name:
                return window.create_view()

    def add_view_for_window_by_nickname(self, nickname):
        for window in self.windows:
            if window.nickname == nickname:
                return window.create_view()

    def pop_window(self):
        self.windows.pop()

    def delete_window_by_id(self, win_id):
        for window in self.windows:
            if window.id == win_id:
                self.windows.remove(window)
                break

    def delete_window_by_name(self, name):
        for window in self.windows:
            if window.name == name:
                self.windows.remove(window)
                break

    def delete_window_by_nickname(self, nickname):
        for window in self.windows:
            if window.nickname == nickname:
                self.windows.remove(window)
                break

    def get_window_by_id(self, win_id):
        for window in self.windows:
            if window.id == win_id:
                return window

        raise(f"No Window by ID {win_id} found!")

    def get_window_by_name(self, name):
        for window in self.windows:
            if window.name == name:
                return window

        raise(f"No Window by Name {name} found!")

    def get_window_by_nickname(self, nickname):
        for window in self.windows:
            if window.nickname == nickname:
                return window

        raise(f"No Window by Nickname {nickname} found!")

    def get_window_by_index(self, index):
        return self.windows[index]

    def get_all_windows(self):
        return self.windows

    def set_window_nickname(self, win_id = None, nickname = ""):
        for window in self.windows:
            if window.id == win_id:
                window.nickname = nickname

    def list_windows(self):
        print("\n[  ----  Windows  ----  ]\n")
        for window in self.windows:
            print(f"\nID: {window.id}")
            print(f"Name: {window.name}")
            print(f"Nickname: {window.nickname}")
            print(f"Is Hidden: {window.isHidden}")
            print(f"View Count: {window.get_views_count()}")
        print("\n-------------------------\n")



    def list_files_from_views_of_window(self, win_id):
        for window in self.windows:
            if window.id == win_id:
                window.list_files_from_views()
                break

    def get_views_count(self, win_id):
        for window in self.windows:
            if window.id == win_id:
                return window.get_views_count()

    def get_views_from_window(self, win_id):
        for window in self.windows:
            if window.id == win_id:
                return window.get_all_views()




    def save_state(self):
        windows = []
        for window in self.windows:
            views = []
            for view in window.views:
                views.append(view.get_current_directory())

            windows.append(
                [
                    {
                        'window':{
                            "ID": window.id,
                            "Name": window.name,
                            "Nickname": window.nickname,
                            "isHidden": f"{window.isHidden}",
                            'views': views
                        }
                    }
                ]
            )

        with open(self.session_file, 'w') as outfile:
            json.dump(windows, outfile, separators=(',', ':'), indent=4)

    def load_state(self):
        if path.isfile(self.session_file):
            with open(self.session_file) as infile:
                return json.load(infile)
