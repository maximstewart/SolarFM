# Python imports

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Application imports
from shellfm.windows.tabs.tab import Tab
from .icon_view import IconView




class FileView(Gtk.ScrolledWindow):
    """docstring for FileView."""

    def __init__(self):
        super(FileView, self).__init__()
        self.tab_state  = Tab()
        self.icon_view  = IconView(self.tab_state)
        self.tab_widget = self.create_tab_widget()

        self._setup_styling()
        self._setup_signals()

        self.add(self.icon_view)
        self.show_all()


    def _setup_styling(self):
        self.set_hexpand(True)
        self.set_vexpand(True)

    def _setup_signals(self):
        # self.connect("update-tab-title", self._update_tab_title)
        ...

    def _update_tab_title(self, widget=None, eve=None):
        label = self.tab_widget.get_children()[0]
        label.set_label(f"{self.tab_state.get_end_of_path()}")
        label.set_width_chars( len(self.tab_state.get_end_of_path()) )

    def set_path(self, path):
        if path:
            self.tab_state.set_path(path)
            self.icon_view.load_store()
            self._update_tab_title()

    def create_tab_widget(self):
        button_box = Gtk.ButtonBox()
        label      = Gtk.Label()
        close      = Gtk.Button()
        icon       = Gtk.Image(stock=Gtk.STOCK_CLOSE)

        label.set_label(f"{self.tab_state.get_end_of_path()}")
        label.set_width_chars(len(self.tab_state.get_end_of_path()))
        label.set_xalign(0.0)

        close.add(icon)
        button_box.add(label)
        button_box.add(close)

        close.connect("released", self.close_tab)

        button_box.show_all()
        return button_box


    def close_tab(self, widget, eve=None):
        self.get_parent().emit('close-view', (self,))
