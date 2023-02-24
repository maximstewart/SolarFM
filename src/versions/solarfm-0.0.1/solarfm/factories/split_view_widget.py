# Python imports

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Application imports
from core.widgets.fm_widget.files_widget import FilesWidget




class SplitViewWidget(Gtk.Paned):
    def __init__(self):
        super(SplitViewWidget, self).__init__()

        self._setup_styling()
        self._setup_signals()
        self._load_widgets()

        self.show_all()


    def _setup_styling(self):
        self.set_wide_handle(True)

    def _setup_signals(self):
        ...

    def _load_widgets(self):
        self.pack1(FilesWidget(), resize=False, shrink=False)
        self.pack2(FilesWidget(), resize=True, shrink=False)
