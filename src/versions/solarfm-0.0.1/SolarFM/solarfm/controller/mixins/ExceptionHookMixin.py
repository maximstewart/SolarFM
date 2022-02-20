# Python imports
import traceback, threading, time

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

# Application imports


def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs, daemon=True).start()
    return wrapper


class ExceptionHookMixin:
    ''' ExceptionHookMixin custom exception hook to reroute to a Gtk text area. '''

    def custom_except_hook(self, exec_type, value, _traceback):
        trace     = ''.join(traceback.format_tb(_traceback))
        data      = f"Exec Type:  {exec_type}  <-->  Value:  {value}\n\n{trace}\n\n\n\n"
        start_itr = self.message_buffer.get_start_iter()
        self.message_buffer.place_cursor(start_itr)
        self.display_message(self.error, data)

    def display_message(self, type, text, seconds=None):
        self.message_buffer.insert_at_cursor(text)
        self.message_widget.popup()
        if seconds:
            self.hide_message_timeout(seconds)

    @threaded
    def hide_message_timeout(self, seconds=3):
        time.sleep(seconds)
        GLib.idle_add(self.message_widget.popdown)

    def save_debug_alerts(self, widget=None, eve=None):
        start_itr, end_itr   = self.message_buffer.get_bounds()
        save_location_prompt = Gtk.FileChooserDialog("Choose Save Folder", self.window, \
                                                        action  = Gtk.FileChooserAction.SAVE, \
                                                        buttons = (Gtk.STOCK_CANCEL, \
                                                                    Gtk.ResponseType.CANCEL, \
                                                                    Gtk.STOCK_SAVE, \
                                                                    Gtk.ResponseType.OK))

        text = self.message_buffer.get_text(start_itr, end_itr, False)
        resp = save_location_prompt.run()
        if (resp == Gtk.ResponseType.CANCEL) or (resp == Gtk.ResponseType.DELETE_EVENT):
            pass
        elif resp == Gtk.ResponseType.OK:
            target = save_location_prompt.get_filename();
            with open(target, "w") as f:
                f.write(text)

        save_location_prompt.destroy()


    def set_arc_buffer_text(self, widget=None, eve=None):
        sid = widget.get_active_id()
        self.arc_command_buffer.set_text(self.arc_commands[int(sid)])
