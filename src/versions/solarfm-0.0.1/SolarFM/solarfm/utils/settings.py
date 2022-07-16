# Python imports
import os, json
from os import path

# Gtk imports
import gi, cairo
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')

from gi.repository import Gtk
from gi.repository import Gdk


# Application imports
from .logger import Logger
from .keybindings import Keybindings




class Settings:
    def __init__(self):
        self._SCRIPT_PTH    = os.path.dirname(os.path.realpath(__file__))
        self._USER_HOME     = path.expanduser('~')
        self._CONFIG_PATH   = f"{self._USER_HOME}/.config/{app_name.lower()}"
        self._PLUGINS_PATH  = f"{self._CONFIG_PATH}/plugins"
        self._USR_SOLARFM   = f"/usr/share/{app_name.lower()}"

        self._CSS_FILE      = f"{self._CONFIG_PATH}/stylesheet.css"
        self._GLADE_FILE    = f"{self._CONFIG_PATH}/Main_Window.glade"
        self._KEY_BINDINGS  = f"{self._CONFIG_PATH}/key-bindings.json"
        self._DEFAULT_ICONS = f"{self._CONFIG_PATH}/icons"
        self._WINDOW_ICON   = f"{self._DEFAULT_ICONS}/{app_name.lower()}.png"
        self._ICON_THEME    = Gtk.IconTheme.get_default()

        if not os.path.exists(self._CONFIG_PATH):
            os.mkdir(self._CONFIG_PATH)
        if not os.path.exists(self._PLUGINS_PATH):
            os.mkdir(self._PLUGINS_PATH)

        if not os.path.exists(self._GLADE_FILE):
            self._GLADE_FILE    = f"{self._USR_SOLARFM}/Main_Window.glade"
        if not os.path.exists(self._KEY_BINDINGS):
            self._KEY_BINDINGS  = f"{self._USR_SOLARFM}/key-bindings.json"
        if not os.path.exists(self._CSS_FILE):
            self._CSS_FILE      = f"{self._USR_SOLARFM}/stylesheet.css"
        if not os.path.exists(self._WINDOW_ICON):
            self._WINDOW_ICON   = f"{self._USR_SOLARFM}/icons/{app_name.lower()}.png"
        if not os.path.exists(self._DEFAULT_ICONS):
            self._DEFAULT_ICONS = f"{self._USR_SOLARFM}/icons"

        self._success_color = "#88cc27"
        self._warning_color = "#ffa800"
        self._error_color   = "#ff0000"

        self._keybindings = Keybindings()
        with open(self._KEY_BINDINGS) as file:
            keybindings = json.load(file)["keybindings"]
            self._keybindings.configure(keybindings)

        self._main_window    = None
        self._logger         = Logger(self._CONFIG_PATH, _fh_log_lvl=20).get_logger()
        self._builder        = Gtk.Builder()
        self._builder.add_from_file(self._GLADE_FILE)


    def create_window(self) -> None:
        # Get window and connect signals
        self._main_window = self._builder.get_object("main_window")
        self._set_window_data()

    def _set_window_data(self) -> None:
        self._main_window.set_icon_from_file(self._WINDOW_ICON)
        screen = self._main_window.get_screen()
        visual = screen.get_rgba_visual()

        if visual != None and screen.is_composited():
            self._main_window.set_visual(visual)
            self._main_window.set_app_paintable(True)
            self._main_window.connect("draw", self._area_draw)

        # bind css file
        cssProvider  = Gtk.CssProvider()
        cssProvider.load_from_path(self._CSS_FILE)
        screen       = Gdk.Screen.get_default()
        styleContext = Gtk.StyleContext()
        styleContext.add_provider_for_screen(screen, cssProvider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

    def _area_draw(self, widget: Gtk.ApplicationWindow, cr: cairo.Context) -> None:
        cr.set_source_rgba(0, 0, 0, 0.54)
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)

    def get_monitor_data(self) -> list:
        screen = self._builder.get_object("main_window").get_screen()
        monitors = []
        for m in range(screen.get_n_monitors()):
            monitors.append(screen.get_monitor_geometry(m))
            print("{}x{}+{}+{}".format(monitor.width, monitor.height, monitor.x, monitor.y))

        return monitors

    def get_main_window(self)   -> Gtk.ApplicationWindow: return self._main_window
    def get_builder(self)       -> Gtk.Builder:  return self._builder
    def get_logger(self)        -> Logger:       return self._logger
    def get_keybindings(self)   -> Keybindings:  return self._keybindings
    def get_plugins_path(self)  -> str:          return self._PLUGINS_PATH
    def get_icon_theme(self)    -> str:          return self._ICON_THEME

    def get_success_color(self) -> str: return self._success_color
    def get_warning_color(self) -> str: return self._warning_color
    def get_error_color(self)   -> str: return self._error_color
