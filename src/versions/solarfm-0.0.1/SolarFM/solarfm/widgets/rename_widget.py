# Python imports

# Lib imports
import inspect
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
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
        edit_file_menu   = self._builder.get_object("edit_file_menu")
        new_rename_fname = self._builder.get_object("new_rename_fname")
        file_to_rename_label = self._builder.get_object("file_to_rename_label")

        builder.expose_object(f"edit_file_menu", edit_file_menu)
        builder.expose_object(f"new_rename_fname", new_rename_fname)
        builder.expose_object(f"file_to_rename_label", file_to_rename_label)

        self._setup_styling()
        self._setup_signals()
        self._load_widgets()


    def _setup_styling(self):
        ...

    def _setup_signals(self):
        event_system.subscribe("do_hide_edit_file_menu", self.hide_edit_file_menu)

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

    def set_to_title_case(self, widget, eve=None):
        rename_widget = self._builder.get_object("new_rename_fname")
        rename_widget.set_text( rename_widget.get_text().title() )

    def set_to_upper_case(self, widget, eve=None):
        rename_widget = self._builder.get_object("new_rename_fname")
        rename_widget.set_text( rename_widget.get_text().upper() )

    def set_to_lower_case(self, widget, eve=None):
        rename_widget = self._builder.get_object("new_rename_fname")
        rename_widget.set_text( rename_widget.get_text().lower() )

    def set_to_invert_case(self, widget, eve=None):
        rename_widget = self._builder.get_object("new_rename_fname")
        rename_widget.set_text( rename_widget.get_text().swapcase() )

    def hide_edit_file_menu(self, widget=None, eve=None):
        self._builder.get_object("edit_file_menu").hide()

    def hide_edit_file_menu_enter_key(self, widget=None, eve=None):
        keyname = Gdk.keyval_name(eve.keyval).lower()
        if keyname in ["return", "enter"]:
            self._builder.get_object("edit_file_menu").hide()
