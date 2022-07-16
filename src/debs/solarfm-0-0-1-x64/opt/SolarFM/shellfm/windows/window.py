# Python imports
from random import randint


# Lib imports


# Application imports
from .tabs.tab import Tab


class Window:
    def __init__(self):
        self._id_length = 10
        self._id        = ""
        self._name      = ""
        self._nickname  = ""
        self._isHidden  = False
        self._tabs      = []

        self._generate_id()
        self._set_name()


    def create_tab(self):
        tab = Tab()
        self._tabs.append(tab)
        return tab

    def pop_tab(self):
        self._tabs.pop()

    def delete_tab_by_id(self, vid):
        for tab in self._tabs:
            if tab.get_id() == vid:
                self._tabs.remove(tab)
                break


    def get_tab_by_id(self, vid):
        for tab in self._tabs:
            if tab.get_id() == vid:
                return tab

    def get_tab_by_index(self, index):
        return self._tabs[index]

    def get_tabs_count(self):
        return len(self._tabs)

    def get_all_tabs(self):
        return self._tabs

    def get_id(self):
        return self._id

    def get_name(self):
        return self._name

    def get_nickname(self):
        return self._nickname

    def is_hidden(self):
        return self._isHidden

    def list_files_from_tabs(self):
        for tab in self._tabs:
            print(tab.get_files())


    def set_nickname(self, nickname):
        self._nickname = f"{nickname}"

    def set_is_hidden(self, state):
        self._isHidden = f"{state}"

    def _set_name(self):
        self._name = "window_" + self.get_id()


    def _random_with_N_digits(self, n):
        range_start = 10**(n-1)
        range_end = (10**n)-1
        return randint(range_start, range_end)

    def _generate_id(self):
        self._id = str(self._random_with_N_digits(self._id_length))
