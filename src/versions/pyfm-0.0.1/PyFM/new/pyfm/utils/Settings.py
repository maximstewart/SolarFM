# Python imports
import os

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
        self.SCRIPT_PTH = os.path.dirname(os.path.realpath(__file__))
        self.gladefile  = self.SCRIPT_PTH + "/../resources/Main_Window.glade"
        self.cssFile    = self.SCRIPT_PTH + '/../resources/stylesheet.css'
        self.logger     = Logger().get_logger()

        self.builder    = gtk.Builder()
        self.builder.add_from_file(self.gladefile)
        self.mainWindow = None



    def createWindow(self):
        # Get window and connect signals
        self.mainWindow = self.builder.get_object("Main_Window")
        self.setWindowData()

    def setWindowData(self):
        screen = self.mainWindow.get_screen()
        visual = screen.get_rgba_visual()

        if visual != None and screen.is_composited():
            self.mainWindow.set_visual(visual)
            self.mainWindow.set_app_paintable(True)
            self.mainWindow.connect("draw", self.area_draw)

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

    def getMainWindow(self):  return self.mainWindow


    def getMonitorData(self):
        screen = self.builder.get_object("Main_Window").get_screen()
        monitors = []
        for m in range(screen.get_n_monitors()):
            monitors.append(screen.get_monitor_geometry(m))

        for monitor in monitors:
            print("{}x{}+{}+{}".format(monitor.width, monitor.height, monitor.x, monitor.y))

        return monitors
