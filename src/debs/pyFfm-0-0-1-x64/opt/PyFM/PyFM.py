#!/usr/bin/python3

# Gtk Imports
import gi, faulthandler
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.0')

from gi.repository import Gtk as gtk
from gi.repository import Gdk as gdk
from gi.repository import WebKit2 as webkit

# Python imports
from utils import Settings, Events

gdk.threads_init()
class Main:
    def __init__(self):
        faulthandler.enable()
        webkit.WebView()  # Needed for glade file to load...

        self.builder     = gtk.Builder()
        self.settings    = Settings()
        self.settings.attachBuilder(self.builder)
        self.builder.connect_signals(Events(self.settings))

        window = self.settings.createWindow()
        window.fullscreen()
        window.show_all()


if __name__ == "__main__":
    try:
        main = Main()
        gtk.main()
    except Exception as e:
        print(e)
