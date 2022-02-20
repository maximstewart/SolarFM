# Python imports
from random import randint


# Lib imports


# Application imports
from .views.view import View


class Window:
    def __init__(self):
        self._id_length = 10
        self._id        = ""
        self._name      = ""
        self._nickname  = ""
        self._isHidden  = False
        self._views     = []

        self._generate_id()
        self._set_name()


    def create_view(self):
        view = View()
        self._views.append(view)
        return view

    def pop_view(self):
        self._views.pop()

    def delete_view_by_id(self, vid):
        for view in self._views:
            if view.get_id() == vid:
                self._views.remove(view)
                break


    def get_view_by_id(self, vid):
        for view in self._views:
            if view.get_id() == vid:
                return view

    def get_view_by_index(self, index):
        return self._views[index]

    def get_views_count(self):
        return len(self._views)

    def get_all_views(self):
        return self._views

    def list_files_from_views(self):
        for view in self._views:
            print(view.get_files())


    def get_id(self):
        return self._id

    def get_name(self):
        return self._name

    def get_nickname(self):
        return self._nickname

    def is_hidden(self):
        return self._isHidden




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
