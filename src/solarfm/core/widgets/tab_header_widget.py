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

        self._close_tab = close_tab # NOTE: Close method is from tab_mixin

        self._setup_styling()
        self._setup_signals()
        self._load_widgets()


    def _setup_styling(self):
        self.set_orientation(0)
        self.set_hexpand(False)

    def _setup_signals(self):
        ...

    def _load_widgets(self):
        self.label     = Gtk.Label()
        self.close_btn = Gtk.Button()
        icon           = Gtk.Image(stock = Gtk.STOCK_CLOSE)

        self.label.set_xalign(0.0)
        self.label.set_margin_left(25)
        self.label.set_margin_right(25)
        self.label.set_hexpand(True)

        self._handler_id = self.close_btn.connect("released", self._close_tab)

        self.close_btn.add(icon)
        self.add(self.label)
        self.add(self.close_btn)

        self.show_all()

    def clear_signals_and_data(self):
        self.close_btn.disconnect(self._handler_id)
        self._close_tab    = None
        self._handler_id   = None

        for child in self.get_children():
            child.unparent()
            child.run_dispose()
