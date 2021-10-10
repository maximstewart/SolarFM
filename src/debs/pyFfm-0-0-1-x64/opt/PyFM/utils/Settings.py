
# Gtk Imports
import gi, cairo, os
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')

from gi.repository import Gtk as gtk
from gi.repository import Gdk as gdk

class Settings:
    def __init__(self):
        self.builder            = None
        self.hideHiddenFiles    = True


        self.GTK_ORIENTATION    = 1   # HORIZONTAL (0) VERTICAL (1)
        self.THUMB_GENERATOR    = "ffmpegthumbnailer"
        self.DEFAULTCOLOR       = gdk.RGBA(0.0, 0.0, 0.0, 0.0)   # ~#00000000
        self.MOUSEOVERCOLOR     = gdk.RGBA(0.0, 0.9, 1.0, 0.64)  # ~#00e8ff
        self.SELECTEDCOLOR      = gdk.RGBA(0.4, 0.5, 0.1, 0.84)

        self.ColumnSize         = 8
        self.usrHome            = os.path.expanduser('~')
        self.desktopPath        = self.usrHome + "/Desktop"
        self.webHome            = 'http://webfm.com/'
        self.iconContainerWxH   = [128, 128]
        self.systemIconImageWxH = [72, 72]
        self.viIconWxH          = [256, 128]
        self.vidsExtensionList   = ('.mkv', '.avi', '.flv', '.mov', '.m4v', '.mpg', '.wmv', '.mpeg', '.mp4', '.webm')
        self.imagesExtensionList = ('.png', '.jpg', '.jpeg', '.gif', '.ico', '.tga')


    def attachBuilder(self, builder):
        self.builder = builder
        self.builder.add_from_file("resources/PyTop.glade")

    def createWindow(self):
        # Get window and connect signals
        window = self.builder.get_object("Window")
        window.connect("delete-event", gtk.main_quit)
        self.setWindowData(window)
        return window

    def setWindowData(self, window):
        screen = window.get_screen()
        visual = screen.get_rgba_visual()
        if visual != None and screen.is_composited():
            window.set_visual(visual)

        # bind css file
        cssProvider = gtk.CssProvider()
        cssProvider.load_from_path('resources/stylesheet.css')
        screen = gdk.Screen.get_default()
        styleContext = gtk.StyleContext()
        styleContext.add_provider_for_screen(screen, cssProvider, gtk.STYLE_PROVIDER_PRIORITY_USER)

        window.set_app_paintable(True)
        monitors = self.getMonitorData(screen)
        window.resize(monitors[0].width, monitors[0].height)

    def getMonitorData(self, screen):
        monitors = []
        for m in range(screen.get_n_monitors()):
            monitors.append(screen.get_monitor_geometry(m))

        for monitor in monitors:
            print(str(monitor.width) + "x" + str(monitor.height) + "+" + str(monitor.x) + "+" + str(monitor.y))

        return monitors


    def returnBuilder(self):             return self.builder
    def returnUserHome(self):            return self.usrHome
    def returnDesktopPath(self):         return self.usrHome + "/Desktop"
    def returnIconImagePos(self):        return self.GTK_ORIENTATION
    def getThumbnailGenerator(self):     return self.THUMB_GENERATOR
    def returnColumnSize(self):          return self.ColumnSize
    def returnContainerWH(self):         return self.iconContainerWxH
    def returnSystemIconImageWH(self):   return self.systemIconImageWxH
    def returnVIIconWH(self):            return self.viIconWxH
    def returnWebHome(self):             return self.webHome
    def isHideHiddenFiles(self):         return self.hideHiddenFiles
    def returnVidsExtensionList(self):   return self.vidsExtensionList
    def returnImagesExtensionList(self): return self.imagesExtensionList

    def setDefaultWebviewSettings(self, widget, settings=None):
        # Usability
        settings.set_property('enable-fullscreen', True)
        settings.set_property('print-backgrounds', True)
        settings.set_property('enable-frame-flattening', False)
        settings.set_property('enable-plugins', True)
        settings.set_property('enable-java', False)
        settings.set_property('enable-resizable-text-areas', True)
        settings.set_property('zoom-text-only', False)
        settings.set_property('enable-smooth-scrolling', True)
        settings.set_property('enable-back-forward-navigation-gestures', False)
        settings.set_property('media-playback-requires-user-gesture', False)
        settings.set_property('enable-tabs-to-links', True)
        settings.set_property('enable-caret-browsing', False)

        # Security
        settings.set_property('user-agent','Mozilla/5.0 (X11; Generic; Linux x86-64) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.0 Safari/605.1.15')
        settings.set_property('enable-private-browsing', False)
        settings.set_property('enable-xss-auditor', True)
        settings.set_property('enable-hyperlink-auditing', False)
        settings.set_property('enable-site-specific-quirks', True)
        settings.set_property('enable-offline-web-application-cache', True)
        settings.set_property('enable-page-cache', True)
        settings.set_property('allow-modal-dialogs', False)
        settings.set_property('enable-html5-local-storage', True)
        settings.set_property('enable-html5-database', True)
        settings.set_property('allow-file-access-from-file-urls', False)
        settings.set_property('allow-universal-access-from-file-urls', False)
        settings.set_property('enable-dns-prefetching', False)

        # Media stuff
        # settings.set_property('hardware-acceleration-policy', 'on-demand')
        settings.set_property('enable-webgl', False)
        settings.set_property('enable-webaudio', True)
        settings.set_property('enable-accelerated-2d-canvas', True)
        settings.set_property('auto-load-images', True)
        settings.set_property('enable-media-capabilities', True)
        settings.set_property('enable-media-stream', True)
        settings.set_property('enable-mediasource', True)
        settings.set_property('enable-encrypted-media', True)
        settings.set_property('media-playback-allows-inline', True)

        # JS
        settings.set_property('enable-javascript', True)
        settings.set_property('enable-javascript-markup', True)
        settings.set_property('javascript-can-access-clipboard', False)
        settings.set_property('javascript-can-open-windows-automatically', False)

        # Debugging
        settings.set_property('enable-developer-extras', False)
        settings.set_property('enable-write-console-messages-to-stdout', False)
        settings.set_property('draw-compositing-indicators', False)
        settings.set_property('enable-mock-capture-devices', False)
        settings.set_property('enable-spatial-navigation', False)
