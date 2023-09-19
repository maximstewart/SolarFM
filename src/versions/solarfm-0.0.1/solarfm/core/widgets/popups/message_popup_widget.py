# Python imports
import datetime
import inspect
import sys
import time
import traceback

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GLib

# Application imports




class MessagePopupWidget(Gtk.Popover):
    """ MessagePopupWidget custom exception hook viewer to reroute to log Gtk text area too. """


    def __init__(self):
        super(MessagePopupWidget, self).__init__()

        self.builder = settings_manager.get_builder()
        self.builder.expose_object(f"message_popup_widget", self)

        self._message_buffer = None

        sys.excepthook = self.custom_except_hook

        self._setup_styling()
        self._setup_signals()
        self._load_widgets()


    def _setup_styling(self):
        self.set_relative_to( self.builder.get_object(f"main_menu_bar") )
        self.set_modal(True)
        self.set_position(Gtk.PositionType.BOTTOM)
        self.set_hexpand(True)
        self.set_vexpand(True)

    def _setup_signals(self):
        event_system.subscribe("show_messages_popup", self.show_messages_popup)
        event_system.subscribe("hide_messages_popup", self.hide_messages_popup)

    def _load_widgets(self):
        self._message_buffer = Gtk.TextBuffer()
        vbox                 = Gtk.Box()
        scroll_window        = Gtk.ScrolledWindow()
        message_text_view    = Gtk.TextView.new_with_buffer(self._message_buffer)

        button = Gtk.Button(label="Save As")
        button.set_image( Gtk.Image(stock=Gtk.STOCK_SAVE_AS) )
        button.connect("released", self.save_debug_alerts)
        button.set_always_show_image(True)

        scroll_window.set_vexpand(True)
        scroll_window.set_hexpand(True)
        vbox.set_orientation(Gtk.Orientation.VERTICAL)

        self.builder.expose_object(f"message_popup_widget", self)
        self.builder.expose_object(f"message_text_view", message_text_view)

        scroll_window.add(message_text_view)
        vbox.add(button)
        vbox.add(scroll_window)
        vbox.show_all()
        self.add(vbox)


    def show_messages_popup(self):
        self.popup()

    def hide_messages_popup(self):
        self.popup()

    def custom_except_hook(self, exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
        self._exception_to_ui(exc_type, exc_value, exc_traceback)

    def _exception_to_ui(self, exc_type, exc_value, exc_traceback):
        trace        = ''.join(traceback.format_tb(exc_traceback))
        current_time = datetime.datetime.now()
        data         = f"{current_time}\nExec Type:  {exc_type}  <-->  Value:  {exc_value}\n\n{trace}\n\n"

        self.display_message(settings.theming.error_color, data)

    def display_message(self, type, text, seconds=None):
        # start_itr = self._message_buffer.get_start_iter()
        start_itr = self._message_buffer.get_iter_at_line(0)

        self._message_buffer.place_cursor(start_itr)
        self._message_buffer.insert_at_cursor(text)

        if seconds:
            self.popup()
            self.hide_message_timeout(seconds)

    @threaded
    def hide_message_timeout(self, seconds=3):
        time.sleep(seconds)
        GLib.idle_add(event_system.emit, ("hide_messages_popup"))

    def save_debug_alerts(self, widget=None, eve=None):
        start_itr, end_itr   = self._message_buffer.get_bounds()
        save_location_prompt = Gtk.FileChooserDialog("Choose Save Folder", settings_manager.get_main_window(), \
                                                        action  = Gtk.FileChooserAction.SAVE, \
                                                        buttons = (Gtk.STOCK_CANCEL, \
                                                                    Gtk.ResponseType.CANCEL, \
                                                                    Gtk.STOCK_SAVE, \
                                                                    Gtk.ResponseType.OK))

        text = self._message_buffer.get_text(start_itr, end_itr, False)
        resp = save_location_prompt.run()
        if (resp == Gtk.ResponseType.CANCEL) or (resp == Gtk.ResponseType.DELETE_EVENT):
            pass
        elif resp == Gtk.ResponseType.OK:
            target = save_location_prompt.get_filename();
            with open(target, "w") as f:
                f.write(text)

        save_location_prompt.destroy()
