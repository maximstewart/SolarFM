# Python imports

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Application imports




class ContextMenuWidget(Gtk.Menu):
    """docstring for ContextMenuWidget"""

    def __init__(self):
        super(ContextMenuWidget, self).__init__()

        self._builder = Gtk.Builder()

        self._setup_styling()
        self._setup_signals()
        self._load_widgets()


    def _setup_styling(self):
        ...

    def _setup_signals(self):
        event_system.subscribe("show_context_menu", self.show_context_menu)
        event_system.subscribe("hide_context_menu", self.hide_context_menu)
        settings_manager.register_signals_to_builder(self, self._builder)

    def _load_widgets(self):
        self.builder            = settings_manager.get_builder()
        self._window            = settings_manager.get_main_window()
        self._context_menu_data = settings_manager.get_context_menu_data()

        self.builder.expose_object("context_menu", self)

        self.build_context_menu()

    def _emit(self, menu_item, type):
        event_system.emit("do_action_from_menu_controls", type)


    def build_context_menu(self) -> None:
        data          = self._context_menu_data
        plugins_entry = None

        for key, value in data.items():
            entry = self.make_menu_item(key, value)
            self.append(entry)
            if key == "Plugins":
                plugins_entry = entry

        self.attach_to_widget(self._window, None)
        self.show_all()

        if plugins_entry:
            self.builder.expose_object("context_menu_plugins", plugins_entry.get_submenu())

    def make_menu_item(self, label, data) -> Gtk.MenuItem:
        if isinstance(data, dict):
            return self.make_submenu(label, data)
        elif isinstance(data, list):
            entry = Gtk.ImageMenuItem(label)
            icon  = getattr(Gtk, f"{data[0]}")
            entry.set_image( Gtk.Image(stock=icon) )
            entry.set_always_show_image(True)
            entry.connect("activate", self._emit, (data[1]))
            return entry

    def make_submenu(self, name, data):
        menu      = Gtk.Menu()
        menu_item = Gtk.MenuItem(name)

        for key, value in data.items():
            if isinstance(data, dict):
                entry = self.make_menu_item(key, value)
            elif isinstance(data, list):
                entry = self.make_menu_item(key, value)
            else:
                continue

            menu.append(entry)

        menu_item.set_submenu(menu)
        return menu_item


    def show_context_menu(self, widget = None, eve = None):
        self.builder.get_object("context_menu").popup_at_pointer(None)

    def hide_context_menu(self, widget = None, eve = None):
        self.builder.get_object("context_menu").popdown()
