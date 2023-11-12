# Python imports
import time
import signal

# Lib imports
import gi
import cairo
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib

# Application imports
from core.controller import Controller



class ControllerStartException(Exception):
    ...


class Window(Gtk.ApplicationWindow):
    """docstring for Window."""

    def __init__(self, args, unknownargs):
        super(Window, self).__init__()

        self._controller = None
        settings_manager.set_main_window(self)

        self._set_window_data()
        self._setup_styling()
        self._setup_signals()
        self._subscribe_to_events()

        self._load_widgets(args, unknownargs)

        self.show()


    def _setup_styling(self):
        self.set_default_size(settings_manager.get_main_window_width(),
                                settings_manager.get_main_window_height())
        self.set_title(f"{app_name}")
        self.set_icon_from_file( settings_manager.get_window_icon() )
        self.set_gravity(5)  # 5 = CENTER
        self.set_position(1) # 1 = CENTER, 4 = CENTER_ALWAYS

    def _setup_signals(self):
        self.connect("delete-event", self._tear_down)
        GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, self._tear_down)

    def _subscribe_to_events(self):
        event_system.subscribe("tear_down", self._tear_down)
        event_system.subscribe("load_interactive_debug", self._load_interactive_debug)

    def _load_widgets(self, args, unknownargs):
        if settings_manager.is_debug():
            self.set_interactive_debugging(True)

        self._controller = Controller(args, unknownargs)

        if not self._controller:
            raise ControllerStartException("Controller exited and doesn't exist...")

        self.add( self._controller.get_core_widget() )

    def _set_window_data(self) -> None:
        screen = self.get_screen()
        visual = screen.get_rgba_visual()

        if visual != None and screen.is_composited():
            self.set_visual(visual)
            self.set_app_paintable(True)
            self.connect("draw", self._area_draw)

        # bind css file
        cssProvider  = Gtk.CssProvider()
        cssProvider.load_from_path( settings_manager.get_css_file() )
        screen       = Gdk.Screen.get_default()
        styleContext = Gtk.StyleContext()
        styleContext.add_provider_for_screen(screen, cssProvider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

    def _area_draw(self, widget: Gtk.ApplicationWindow, cr: cairo.Context) -> None:
        cr.set_source_rgba( *settings_manager.get_paint_bg_color() )
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)
    
    def _load_interactive_debug(self):
        self.set_interactive_debugging(True)


    def _tear_down(self, widget = None, eve = None):
        event_system.emit("shutting_down")
        settings_manager.clear_pid()
        Gtk.main_quit()