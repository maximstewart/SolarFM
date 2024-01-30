# Python imports

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Application imports



class TabHeaderWidget(Gtk.Box):
    """docstring for TabHeaderWidget"""

    def __init__(self, close_tab):
        super(TabHeaderWidget, self).__init__()

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
        self.label = Gtk.Label()
        close = Gtk.Button()
        icon  = Gtk.Image(stock=Gtk.STOCK_CLOSE)

        self.label.set_xalign(0.0)
        self.label.set_margin_left(25)
        self.label.set_margin_right(25)
        self.label.set_hexpand(True)

        close.connect("released", self._close_tab)

        close.add(icon)
        self.add(self.label)
        self.add(close)

        self.show_all()