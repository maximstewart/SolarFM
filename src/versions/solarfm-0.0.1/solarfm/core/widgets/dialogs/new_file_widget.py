# Python imports
import inspect

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
        builder       = settings.get_builder()
        self._builder = Gtk.Builder()

        self._builder.add_from_file(_GLADE_FILE)
        self._new_file_menu   = self._builder.get_object("new_file_menu")
        self._new_fname_field = self._builder.get_object("new_fname_field")
        self._new_file_toggle_type = self._builder.get_object("new_file_toggle_type")

        builder.expose_object(f"new_file_menu", self._new_file_menu)
        builder.expose_object(f"new_fname_field", self._new_fname_field)
        builder.expose_object(f"new_file_toggle_type", self._new_file_toggle_type)

        self._setup_styling()
        self._setup_signals()
        self._load_widgets()


    def _setup_styling(self):
        ...

    def _setup_signals(self):
        event_system.subscribe("show_new_file_menu", self.show_new_file_menu)
        event_system.subscribe("hide_new_file_menu", self.hide_new_file_menu)

        classes  = [self]
        handlers = {}
        for c in classes:
            methods = None
            try:
                methods = inspect.getmembers(c, predicate=inspect.ismethod)
                handlers.update(methods)
            except Exception as e:
                print(repr(e))

        self._builder.connect_signals(handlers)

    def _load_widgets(self):
        ...

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
