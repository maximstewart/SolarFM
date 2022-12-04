# Python imports

# Lib imports
import inspect
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk

# Application imports




class RenameWidget:
    """docstring for RenameWidget."""

    def __init__(self):
        super(RenameWidget, self).__init__()
        _GLADE_FILE   = f"{settings.get_ui_widgets_path()}/rename_ui.glade"
        builder       = settings.get_builder()
        self._builder = Gtk.Builder()

        self._builder.add_from_file(_GLADE_FILE)
        self._rename_file_menu     = self._builder.get_object("rename_file_menu")
        self._rename_fname         = self._builder.get_object("rename_fname")
        self._file_to_rename_label = self._builder.get_object("file_to_rename_label")

        builder.expose_object(f"rename_file_menu", self._rename_file_menu)
        builder.expose_object(f"rename_fname", self._rename_fname)
        builder.expose_object(f"file_to_rename_label", self._file_to_rename_label)

        self._setup_styling()
        self._setup_signals()
        self._load_widgets()


    def _setup_styling(self):
        ...

    def _setup_signals(self):
        event_system.subscribe("show_rename_file_menu", self.show_rename_file_menu)
        event_system.subscribe("hide_rename_file_menu", self.hide_rename_file_menu)

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

    def show_rename_file_menu(self, widget=None, eve=None):
        if widget:
            widget.grab_focus()

        response = self._rename_file_menu.run()
        if response == Gtk.ResponseType.CLOSE:
            return "skip_edit"
        if response == Gtk.ResponseType.CANCEL:
            return "cancel_edit"

        return ""


    def set_to_title_case(self, widget, eve=None):
        self._rename_fname.set_text( self._rename_fname.get_text().title() )

    def set_to_upper_case(self, widget, eve=None):
        self._rename_fname.set_text( self._rename_fname.get_text().upper() )

    def set_to_lower_case(self, widget, eve=None):
        self._rename_fname.set_text( self._rename_fname.get_text().lower() )

    def set_to_invert_case(self, widget, eve=None):
        self._rename_fname.set_text( self._rename_fname.get_text().swapcase() )

    def hide_rename_file_menu(self, widget=None, eve=None):
        self._rename_file_menu.hide()

    def hide_rename_file_menu_enter_key(self, widget=None, eve=None):
        keyname = Gdk.keyval_name(eve.keyval).lower()
        if keyname in ["return", "enter"]:
            self._rename_file_menu.hide()
