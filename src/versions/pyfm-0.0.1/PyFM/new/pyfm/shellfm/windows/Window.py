# Python imports
from random import randint


# Lib imports


# Application imports
from .view import View


class Window:
    def __init__(self):
        self.id_length = 10
        self.id        = ""
        self.name      = ""
        self.nickname  = ""
        self.isHidden  = False
        self.views     = []

        self.generate_id()


    def random_with_N_digits(self, n):
        range_start = 10**(n-1)
        range_end = (10**n)-1
        return randint(range_start, range_end)

    def generate_id(self):
        self.id = str(self.random_with_N_digits(self.id_length))

    def get_window_id(self):
        return self.id

    def create_view(self):
        view = View()
        self.views.append(view)
        return view

    def pop_view(self):
        self.views.pop()

    def delete_view_by_id(self, vid):
        for view in self.views:
            if view.id == vid:
                self.views.remove(view)
                break


    def get_view_by_id(self, vid):
        for view in self.views:
            if view.id == vid:
                return view

    def get_view_by_index(self, index):
        return self.views[index]

    def get_views_count(self):
        return len(self.views)

    def get_all_views(self):
        return self.views

    def list_files_from_views(self):
        for view in self.views:
            print(view.files)
