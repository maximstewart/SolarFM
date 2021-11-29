# Python imports
import os
from os import path

# Gtk imports
import gi, cairo
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')

from gi.repository import Gtk as gtk
from gi.repository import Gdk as gdk


# Application imports
from . import Logger


class Settings:
    def __init__(self):
        self.SCRIPT_PTH    = os.path.dirname(os.path.realpath(__file__))
        self.USER_HOME     = path.expanduser('~')
        self.CONFIG_PATH   = self.USER_HOME   + "/.config/solarfm"

        self.gladefile     = self.CONFIG_PATH + "/Main_Window.glade"
        self.cssFile       = self.CONFIG_PATH + '/stylesheet.css'
        self.logger        = Logger().get_logger()

        self.builder       = gtk.Builder()
        self.builder.add_from_file(self.gladefile)

        self.DEFAULT_ICONS = self.CONFIG_PATH   + "/icons"
        self.window_icon   = self.DEFAULT_ICONS + "/solarfm.png"
        self.main_window   = None




    def createWindow(self):
        # Get window and connect signals
        self.main_window = self.builder.get_object("Main_Window")
        self.setWindowData()

    def setWindowData(self):
        self.main_window.set_icon_from_file(self.window_icon)
        screen = self.main_window.get_screen()
        visual = screen.get_rgba_visual()

        if visual != None and screen.is_composited():
            self.main_window.set_visual(visual)
            self.main_window.set_app_paintable(True)
            self.main_window.connect("draw", self.area_draw)

        # bind css file
        cssProvider  = gtk.CssProvider()
        cssProvider.load_from_path(self.cssFile)
        screen       = gdk.Screen.get_default()
        styleContext = gtk.StyleContext()
        styleContext.add_provider_for_screen(screen, cssProvider, gtk.STYLE_PROVIDER_PRIORITY_USER)

    def area_draw(self, widget, cr):
        cr.set_source_rgba(0, 0, 0, 0.54)
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)

    def getMainWindow(self):  return self.main_window


    def getMonitorData(self):
        screen = self.builder.get_object("Main_Window").get_screen()
        monitors = []
        for m in range(screen.get_n_monitors()):
            monitors.append(screen.get_monitor_geometry(m))

        for monitor in monitors:
            print("{}x{}+{}+{}".format(monitor.width, monitor.height, monitor.x, monitor.y))

        return monitors
