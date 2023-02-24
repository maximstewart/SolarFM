# Python imports
import inspect

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Application imports




class ContextMenuWidget(Gtk.Menu):
    """docstring for ContextMenuWidget"""

    def __init__(self):
        super(ContextMenuWidget, self).__init__()
        self.builder            = settings.get_builder()
        self._builder           = Gtk.Builder()
        self._context_menu_data = settings.get_context_menu_data()
        self._window            = settings.get_main_window()

        self._setup_styling()
        self._setup_signals()
        self._load_widgets()


    def _setup_styling(self):
        ...

    def _setup_signals(self):
        event_system.subscribe("show_context_menu", self.show_context_menu)
        event_system.subscribe("hide_context_menu", self.hide_context_menu)

        classes  = [self]
        handlers = {}
        for c in classes:
            methods = None
            try:
                methods = inspect.getmembers(c, predicate=inspect.ismethod)
                handlers.update(methods)
            except Exception as e:
                logger.debug(repr(e))

        self._builder.connect_signals(handlers)

    def _load_widgets(self):
        self.build_context_menu()


    def make_submenu(self, name, data, keys):
        menu      = Gtk.Menu()
        menu_item = Gtk.MenuItem(name)

        for key in keys:
            if isinstance(data, dict):
                entry = self.make_menu_item(key, data[key])
            elif isinstance(data, list):
                entry = self.make_menu_item(key, data)
            else:
                continue

            menu.append(entry)

        menu_item.set_submenu(menu)
        return menu_item

    def make_menu_item(self, name, data) -> Gtk.MenuItem:
        if isinstance(data, dict):
            return self.make_submenu(name, data, data.keys())
        elif isinstance(data, list):
            entry = Gtk.ImageMenuItem(name)
            icon  = getattr(Gtk, f"{data[0]}")
            entry.set_image( Gtk.Image(stock=icon) )
            entry.set_always_show_image(True)
            entry.connect("activate", self._emit, (data[1]))
            return entry

    def build_context_menu(self) -> None:
        data          = self._context_menu_data
        dkeys         = data.keys()
        plugins_entry = None

        for dkey in dkeys:
            entry = self.make_menu_item(dkey, data[dkey])
            self.append(entry)
            if dkey == "Plugins":
                plugins_entry = entry

        self.attach_to_widget(self._window, None)
        self.show_all()
        self.builder.expose_object("context_menu", self)
        if plugins_entry:
            self.builder.expose_object("context_menu_plugins", plugins_entry.get_submenu())

    def _emit(self, menu_item, type):
        event_system.emit("do_action_from_menu_controls", type)

    def show_context_menu(self, widget=None, eve=None):
        self.builder.get_object("context_menu").popup_at_pointer(None)

    def hide_context_menu(self, widget=None, eve=None):
        self.builder.get_object("context_menu").popdown()
