# Python imports
import os
from os import path

# Gtk imports
import gi, cairo
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')

from gi.repository import Gtk
from gi.repository import Gdk


# Application imports
from .logger import Logger


class Settings:
    def __init__(self):
        self._SCRIPT_PTH    = os.path.dirname(os.path.realpath(__file__))
        self._USER_HOME     = path.expanduser('~')
        self._CONFIG_PATH   = f"{self._USER_HOME}/.config/{app_name.lower()}"
        self._PLUGINS_PATH  = f"{self._CONFIG_PATH}/plugins"
        self._USR_SOLARFM   = f"/usr/share/{app_name.lower()}"

        self._CSS_FILE      = f"{self._CONFIG_PATH}/stylesheet.css"
        self._WINDOWS_GLADE = f"{self._CONFIG_PATH}/Main_Window.glade"
        self._DEFAULT_ICONS = f"{self._CONFIG_PATH}/icons"
        self._WINDOW_ICON   = f"{self._DEFAULT_ICONS}/{app_name.lower()}.png"

        if not os.path.exists(self._CONFIG_PATH):
            os.mkdir(self._CONFIG_PATH)
        if not os.path.exists(self._PLUGINS_PATH):
            os.mkdir(self._PLUGINS_PATH)

        if not os.path.exists(self._WINDOWS_GLADE):
            self._WINDOWS_GLADE = f"{self._USR_SOLARFM}/Main_Window.glade"
        if not os.path.exists(self._CSS_FILE):
            self._CSS_FILE      = f"{self._USR_SOLARFM}/stylesheet.css"
        if not os.path.exists(self._WINDOW_ICON):
            self._WINDOW_ICON   = f"{self._USR_SOLARFM}/icons/{app_name.lower()}.png"
        if not os.path.exists(self._DEFAULT_ICONS):
            self._DEFAULT_ICONS = f"{self._USR_SOLARFM}/icons"

        self._success_color = "#88cc27"
        self._warning_color = "#ffa800"
        self._error_color   = "#ff0000"

        self.main_window    = None
        self.logger         = Logger(self._CONFIG_PATH).get_logger()
        self.builder        = Gtk.Builder()
        self.builder.add_from_file(self._WINDOWS_GLADE)



    def create_window(self):
        # Get window and connect signals
        self.main_window = self.builder.get_object("Main_Window")
        self._set_window_data()

    def _set_window_data(self):
        self.main_window.set_icon_from_file(self._WINDOW_ICON)
        screen = self.main_window.get_screen()
        visual = screen.get_rgba_visual()

        if visual != None and screen.is_composited():
            self.main_window.set_visual(visual)
            self.main_window.set_app_paintable(True)
            self.main_window.connect("draw", self._area_draw)

        # bind css file
        cssProvider  = Gtk.CssProvider()
        cssProvider.load_from_path(self._CSS_FILE)
        screen       = Gdk.Screen.get_default()
        styleContext = Gtk.StyleContext()
        styleContext.add_provider_for_screen(screen, cssProvider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

    def _area_draw(self, widget, cr):
        cr.set_source_rgba(0, 0, 0, 0.54)
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)

    def get_monitor_data(self):
        screen = self.builder.get_object("Main_Window").get_screen()
        monitors = []
        for m in range(screen.get_n_monitors()):
            monitors.append(screen.get_monitor_geometry(m))

        for monitor in monitors:
            print("{}x{}+{}+{}".format(monitor.width, monitor.height, monitor.x, monitor.y))

        return monitors

    def get_builder(self):       return self.builder
    def get_logger(self):        return self.logger
    def get_main_window(self):   return self.main_window
    def get_plugins_path(self):  return self._PLUGINS_PATH

    def get_success_color(self):  return self._success_color
    def get_warning_color(self):  return self._warning_color
    def get_error_color(self):    return self._error_color
