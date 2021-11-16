from . import TabMixin


class WindowMixin(TabMixin):
    """docstring for WindowMixin"""

    def create_new_view_notebook(self, widget=None, wid=None, path=None):
        self.create_tab(wid, path)
