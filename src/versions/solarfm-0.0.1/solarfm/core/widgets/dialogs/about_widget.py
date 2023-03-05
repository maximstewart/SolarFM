# Python imports

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Application imports




class AboutWidget:
    """docstring for AboutWidget."""

    def __init__(self):
        super(AboutWidget, self).__init__()

        _GLADE_FILE   = f"{settings.get_ui_widgets_path()}/about_ui.glade"
        self._builder = Gtk.Builder()
        self._builder.add_from_file(_GLADE_FILE)

        self._setup_styling()
        self._setup_signals()
        self._load_widgets()


    def _setup_styling(self):
        ...

    def _setup_signals(self):
        event_system.subscribe("show_about_page", self.show_about_page)
        event_system.subscribe("hide_about_page", self.hide_about_page)
        settings.register_signals_to_builder([self,], self._builder)

    def _load_widgets(self):
        builder = settings.get_builder()

        self.about_page = self._builder.get_object("about_page")
        builder.expose_object(f"about_page", self.about_page)


    def show_about_page(self, widget=None, eve=None):
        response   = self.about_page.run()
        if response in [Gtk.ResponseType.CANCEL, Gtk.ResponseType.DELETE_EVENT]:
            self.hide_about_page()

    def hide_about_page(self, widget=None, eve=None):
        self.about_page.hide()
