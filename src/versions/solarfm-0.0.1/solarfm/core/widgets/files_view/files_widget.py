# Python imports

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Application imports
from ...mixins.signals.file_action_signals_mixin import FileActionSignalsMixin
from .window_mixin import WindowMixin



class FilesWidget(FileActionSignalsMixin, WindowMixin):
    """docstring for FilesWidget."""

    ccount = 0

    def __new__(cls, *args, **kwargs):
        obj        = super(FilesWidget, cls).__new__(cls)
        cls.ccount += 1

        return obj

    def __init__(self):
        super(FilesWidget, self).__init__()

        self.INDEX   = self.ccount
        self.NAME    = f"window_{self.INDEX}"
        self.builder = Gtk.Builder()
        self.files_view    = None
        self.fm_controller = None

        self._setup_styling()
        self._setup_signals()
        self._subscribe_to_events()
        self._load_widgets()


    def _setup_styling(self):
        ...

    def _setup_signals(self):
        settings_manager.register_signals_to_builder([self,], self.builder)

    def _subscribe_to_events(self):
        event_system.subscribe("load_files_view_state", self._load_files_view_state)
        event_system.subscribe("get_files_view_icon_grid", self._get_files_view_icon_grid)

    def _load_widgets(self):
        _builder   = settings_manager.get_builder()
        self.files_view = _builder.get_object(f"{self.NAME}")

        self.files_view.set_group_name("files_widget")
        self.builder.expose_object(f"{self.NAME}", self.files_view)

    def _load_files_view_state(self, win_name=None, tabs=None):
        if win_name == self.NAME:
            if tabs:
                for tab in tabs:
                    self.create_new_tab_notebook(None, self.INDEX, tab)
            else:
                self.create_new_tab_notebook(None, self.INDEX, None)

    def _get_files_view_icon_grid(self, win_index=None, tid=None):
        if win_index == str(self.INDEX):
            return self.builder.get_object(f"{self.INDEX}|{tid}|icon_grid")


    def set_fm_controller(self, _fm_controller):
        self.fm_controller = _fm_controller
