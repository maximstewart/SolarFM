# Python imports

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk

# Application imports




class NewFileWidget:
    """docstring for NewFileWidget."""

    def __init__(self):
        super(NewFileWidget, self).__init__()

        _GLADE_FILE   = f"{settings.get_ui_widgets_path()}/new_file_ui.glade"
        self._builder = Gtk.Builder()
        self._builder.add_from_file(_GLADE_FILE)

        self._setup_styling()
        self._setup_signals()
        self._load_widgets()


    def _setup_styling(self):
        ...

    def _setup_signals(self):
        event_system.subscribe("show_new_file_menu", self.show_new_file_menu)
        event_system.subscribe("hide_new_file_menu", self.hide_new_file_menu)
        settings.register_signals_to_builder([self,], self._builder)

    def _load_widgets(self):
        builder = settings.get_builder()

        self._new_file_menu   = self._builder.get_object("new_file_menu")
        self._new_fname_field = self._builder.get_object("new_fname_field")
        self._new_file_toggle_type = self._builder.get_object("new_file_toggle_type")

        builder.expose_object(f"new_file_menu", self._new_file_menu)
        builder.expose_object(f"new_fname_field", self._new_fname_field)
        builder.expose_object(f"new_file_toggle_type", self._new_file_toggle_type)


    def show_new_file_menu(self, widget=None, eve=None):
        if widget:
            widget.set_text("")
            widget.grab_focus()

        response = self._new_file_menu.run()
        if response == Gtk.ResponseType.CANCEL:
            return True
        else:
            return False

    def hide_new_file_menu(self, widget=None, eve=None):
        self._builder.get_object("new_file_menu").hide()

    def hide_new_file_menu_enter_key(self, widget=None, eve=None):
        keyname = Gdk.keyval_name(eve.keyval).lower()
        if keyname in ["return", "enter"]:
            self._new_file_menu.hide()
