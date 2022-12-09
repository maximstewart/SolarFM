# Python imports
import shlex

# Lib imports

# Application imports
from .crud_mixin import CRUDMixin
from .handler_mixin import HandlerMixin




class FileSystemActions(HandlerMixin, CRUDMixin):
    """docstring for FileSystemActions"""

    def __init__(self):
        super(FileSystemActions, self).__init__()
        self._setup_styling()
        self._setup_signals()
        self._subscribe_to_events()
        self._load_widgets()

        self._selected_files = []
        self._to_copy_files  = []
        self._to_cut_files   = []

        self._builder        = settings.get_builder()


    def _setup_styling(self):
        ...

    def _setup_signals(self):
        ...

    def _subscribe_to_events(self):
        event_system.subscribe("set_selected_files", self.set_selected_files)
        event_system.subscribe("get_selected_files", self.get_selected_files)

        event_system.subscribe("open_files", self.open_files)
        event_system.subscribe("open_with_files", self.open_with_files)
        event_system.subscribe("execute_files", self.execute_files)

        event_system.subscribe("cut_files", self.cut_files)
        event_system.subscribe("copy_files", self.copy_files)
        event_system.subscribe("paste_files", self.paste_files)
        event_system.subscribe("move_files", self.move_files)
        event_system.subscribe("copy_name", self.copy_name)
        event_system.subscribe("create_files", self.create_files)
        event_system.subscribe("rename_files", self.rename_files)

    def _load_widgets(self):
        ...


    def set_selected_files(self, selected_files: []):
        self._selected_files = selected_files

    def get_selected_files(self):
        return self._selected_files


    def cut_files(self):
        self._to_copy_files.clear()
        state = event_system.emit_and_await("get_current_state")
        self._to_cut_files = state.uris

    def copy_files(self):
        self._to_cut_files.clear()
        state = event_system.emit_and_await("get_current_state")
        self._to_copy_files = state.uris

    def copy_name(self):
        state = event_system.emit_and_await("get_current_state")
        if len(state.uris) == 1:
            file_name = state.uris[0].split("/")[-1]
            event_system.emit("set_clipboard_data", (file_name,))


    def open_files(self):
        state = event_system.emit_and_await("get_current_state")
        for file in state.uris:
            state.tab.open_file_locally(file)

    def open_with_files(self, app_info):
        state = event_system.emit_and_await("get_current_state")
        state.tab.app_chooser_exec(app_info, state.uris_raw)

    def execute_files(self, in_terminal=False):
        state       = event_system.emit_and_await("get_current_state")
        current_dir = state.tab.get_current_directory()
        command     = None
        for path in state.uris:
            command = f"{shlex.quote(path)}" if not in_terminal else f"{state.tab.terminal_app} -e {shlex.quote(path)}"
            state.tab.execute(shlex.split(command), start_dir=state.tab.get_current_directory())
