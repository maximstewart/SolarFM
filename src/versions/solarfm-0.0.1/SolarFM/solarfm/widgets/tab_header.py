# Python imports

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio

# Application imports


class TabHeader(Gtk.ButtonBox):
    """docstring for TabHeader"""

    def __init__(self, tab, close_tab):
        super(TabHeader, self).__init__()
        self._tab       = tab
        self._close_tab = close_tab # NOTE: Close method in tab_mixin

        self._setup_styling()
        self._setup_signals()
        self._load_widgets()

    def _setup_styling(self):
        self.set_orientation(0)

    def _setup_signals(self):
        ...

    def _load_widgets(self):
        label = Gtk.Label()
        tid   = Gtk.Label()
        close = Gtk.Button()
        icon  = Gtk.Image(stock=Gtk.STOCK_CLOSE)

        label.set_label(f"{self._tab.get_end_of_path()}")
        label.set_width_chars(len(self._tab.get_end_of_path()))
        label.set_xalign(0.0)
        tid.set_label(f"{self._tab.get_id()}")

        close.connect("released", self._close_tab)

        close.add(icon)
        self.add(label)
        self.add(close)
        self.add(tid)

        self.show_all()
        tid.hide()
