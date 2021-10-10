from . import TabMixin


class WindowMixin(TabMixin):
    """docstring for WindowMixin"""

    def create_new_view_notebook(self, widget=None, path=None, wid=None):
        self.create_tab(wid, path, save_state=False)
