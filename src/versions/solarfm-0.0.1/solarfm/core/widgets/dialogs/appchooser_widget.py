# Python imports

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Application imports




class AppchooserWidget:
    """docstring for AppchooserWidget."""

    def __init__(self):
        super(AppchooserWidget, self).__init__()

        _GLADE_FILE   = f"{settings.get_ui_widgets_path()}/appchooser_ui.glade"
        self._builder = Gtk.Builder()
        self._builder.add_from_file(_GLADE_FILE)

        self._setup_styling()
        self._setup_signals()
        self._load_widgets()


    def _setup_styling(self):
        ...

    def _setup_signals(self):
        event_system.subscribe("show_appchooser_menu", self.show_appchooser_menu)
        event_system.subscribe("hide_appchooser_menu", self.hide_appchooser_menu)
        event_system.subscribe("run_appchooser_launch", self.run_appchooser_launch)
        settings.register_signals_to_builder([self,], self._builder)

    def _load_widgets(self):
        builder = settings.get_builder()

        self._appchooser_menu   = self._builder.get_object("appchooser_menu")
        self._appchooser_widget = self._builder.get_object("appchooser_widget")

        builder.expose_object(f"appchooser_menu", self._appchooser_menu)
        builder.expose_object(f"appchooser_widget", self._appchooser_widget)


    def show_appchooser_menu(self, widget=None, eve=None):
        response = self._appchooser_menu.run()
        if response == Gtk.ResponseType.OK:
            app_info = self._appchooser_widget.get_app_info()
            event_system.emit("open_with_files", app_info)
            self.hide_appchooser_menu()
        if response == Gtk.ResponseType.CANCEL:
            self.hide_appchooser_menu()


    def hide_appchooser_menu(self, widget=None, eve=None):
        self._appchooser_menu.hide()

    def run_appchooser_launch(self, widget=None, eve=None):
        self._appchooser_menu.response(Gtk.ResponseType.OK)
