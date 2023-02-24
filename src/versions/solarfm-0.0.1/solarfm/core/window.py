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




class Window(Gtk.ApplicationWindow):
    """docstring for Window."""

    def __init__(self, args, unknownargs):
        super(Window, self).__init__()

        self._controller = None
        settings.set_main_window(self)

        self._set_window_data()
        self._setup_styling()
        self._setup_signals()
        self._subscribe_to_events()

        self._load_widgets(args, unknownargs)

        self.show()


    def _setup_styling(self):
        self.set_default_size(1670, 830)
        self.set_title(f"{app_name}")
        self.set_icon_from_file( settings.get_window_icon() )
        self.set_gravity(5)  # 5 = CENTER
        self.set_position(1) # 1 = CENTER, 4 = CENTER_ALWAYS

    def _setup_signals(self):
        self.connect("delete-event", self._tear_down)

        # self.connect("focus-out-event", self._controller.unset_keys_and_data)
        # self.connect("key-press-event", self._controller.on_global_key_press_controller)
        # self.connect("key-release-event", self._controller.on_global_key_release_controller)

        GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, self._tear_down)

    def _subscribe_to_events(self):
        event_system.subscribe("tear_down", self._tear_down)

    def _load_widgets(self, args, unknownargs):
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
        cssProvider.load_from_path( settings.get_css_file() )
        screen       = Gdk.Screen.get_default()
        styleContext = Gtk.StyleContext()
        styleContext.add_provider_for_screen(screen, cssProvider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

    def _area_draw(self, widget: Gtk.ApplicationWindow, cr: cairo.Context) -> None:
        cr.set_source_rgba(0, 0, 0, 0.54)
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)


    def _tear_down(self, widget=None, eve=None):
        if not settings.is_trace_debug():
            self._controller.fm_controller.save_state()

        settings.clear_pid()
        time.sleep(event_sleep_time)
        Gtk.main_quit()
