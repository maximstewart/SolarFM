# Python imports

# Lib imports
import inspect
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Application imports




class AboutWidget:
    """docstring for AboutWidget."""

    def __init__(self):
        super(AboutWidget, self).__init__()
        _GLADE_FILE   = f"{settings.get_ui_widgets_path()}/about_ui.glade"
        builder       = settings.get_builder()
        self._builder = Gtk.Builder()

        self._builder.add_from_file(_GLADE_FILE)
        self.about_page = self._builder.get_object("about_page")

        builder.expose_object(f"about_page", self.about_page)

        self._setup_styling()
        self._setup_signals()
        self._load_widgets()


    def _setup_styling(self):
        ...

    def _setup_signals(self):
        event_system.subscribe("show_about_page", self.show_about_page)
        event_system.subscribe("hide_about_page", self.hide_about_page)

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

    def show_about_page(self, widget=None, eve=None):
        response   = self.about_page.run()
        if response in [Gtk.ResponseType.CANCEL, Gtk.ResponseType.DELETE_EVENT]:
            self.hide_about_page()

    def hide_about_page(self, widget=None, eve=None):
        self.about_page.hide()
