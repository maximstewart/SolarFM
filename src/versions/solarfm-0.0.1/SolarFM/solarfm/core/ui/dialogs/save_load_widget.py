# Python imports
import inspect
import gc

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Application imports




class SaveLoadWidget:
    """docstring for SaveLoadWidget."""

    def __init__(self):
        super(SaveLoadWidget, self).__init__()
        _GLADE_FILE   = f"{settings.get_ui_widgets_path()}/save_load_ui.glade"
        builder       = settings.get_builder()
        self._builder = Gtk.Builder()

        self._builder.add_from_file(_GLADE_FILE)
        self.save_load_dialog = self._builder.get_object("save_load_dialog")

        builder.expose_object(f"save_load_dialog", self.save_load_dialog)

        self._setup_styling()
        self._setup_signals()
        self._load_widgets()


    def _setup_styling(self):
        ...

    def _setup_signals(self):
        event_system.subscribe("save_load_session", self.save_load_session)

    def _load_widgets(self):
        ...


    def save_load_session(self, action="save_session"):
        state = event_system.emit_and_await("get_current_state")

        if action == "save_session":
            if not settings.is_trace_debug():
                state.fm_controller.save_state()

            return
        elif action == "save_session_as":
            self.save_load_dialog.set_action(Gtk.FileChooserAction.SAVE)
        elif action == "load_session":
            self.save_load_dialog.set_action(Gtk.FileChooserAction.OPEN)
        else:
            raise Exception(f"Unknown action given:  {action}")

        self.save_load_dialog.set_current_folder(state.tab.get_current_directory())
        self.save_load_dialog.set_current_name("session.json")
        response = self.save_load_dialog.run()
        if response == Gtk.ResponseType.OK:
            if action == "save_session_as":
                path = f"{self.save_load_dialog.get_current_folder()}/{self.save_load_dialog.get_current_name()}"
                state.fm_controller.save_state(path)
            elif action == "load_session":
                path         = f"{self.save_load_dialog.get_file().get_path()}"
                session_json = state.fm_controller.get_state_from_file(path)
                self.load_session(session_json)
        if (response == Gtk.ResponseType.CANCEL) or (response == Gtk.ResponseType.DELETE_EVENT):
            ...

        self.save_load_dialog.hide()

    def load_session(self, session_json):
        if settings.is_debug():
            logger.debug(f"Session Data: {session_json}")

        state = event_system.emit_and_await("get_current_state")
        event_system.emit("clear_notebooks")
        state.fm_controller.unload_tabs_and_windows()
        event_system.emit("generate_windows", (session_json,))
        gc.collect()
