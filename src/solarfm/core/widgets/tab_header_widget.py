# Python imports

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Application imports




class TabHeaderWidget(Gtk.Box):
    """docstring for TabHeaderWidget"""

    def __init__(self, tab, close_tab):
        super(TabHeaderWidget, self).__init__()

        self._tab       = tab
        self._close_tab = close_tab # NOTE: Close method in tab_mixin

        self._setup_styling()
        self._setup_signals()
        self._load_widgets()


    def _setup_styling(self):
        self.set_orientation(0)
        self.set_hexpand(False)

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
        label.set_margin_left(25)
        label.set_margin_right(25)
        label.set_hexpand(True)
        tid.set_label(f"{self._tab.get_id()}")

        close.connect("released", self._close_tab)

        close.add(icon)
        self.add(label)
        self.add(close)
        self.add(tid)

        self.show_all()
        tid.hide()
