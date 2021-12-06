# Python imports
import sys, traceback, threading, subprocess, signal, inspect, os, time

# Gtk imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GLib

# Application imports
from .mixins import *
from . import ShowHideMixin, KeyboardSignalsMixin, Controller_Data


def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()
    return wrapper


class Controller(Controller_Data, ShowHideMixin, KeyboardSignalsMixin, \
                            WidgetFileActionMixin, PaneMixin, WindowMixin):
    def __init__(self, args, unknownargs, _settings):
        # sys.excepthook = self.custom_except_hook
        self.settings  = _settings
        self.setup_controller_data()

        self.window.show()
        self.generate_windows(self.state)

        self.window.connect("delete-event", self.tear_down)
        GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, self.tear_down)
        self.gui_event_observer()

        if unknownargs:
            for arg in unknownargs:
                if os.path.isdir(arg):
                    message = f"FILE|{arg}"
                    event_system.send_ipc_message(message)

        if args.new_tab and os.path.isdir(args.new_tab):
            message = f"FILE|{args.new_tab}"
            event_system.send_ipc_message(message)


    def tear_down(self, widget=None, eve=None):
        event_system.monitor_events  = False
        event_system.send_ipc_message("close server")
        self.window_controller.save_state()
        time.sleep(event_sleep_time)
        Gtk.main_quit()


    @threaded
    def gui_event_observer(self):
        while event_system.monitor_events:
            time.sleep(event_sleep_time)
            event = event_system.consume_gui_event()
            if event:
                try:
                    type, target, data = event
                    method = getattr(self.__class__, type)
                    GLib.idle_add(method, (self, data,))
                except Exception as e:
                    print(repr(e))


    def custom_except_hook(self, exctype, value, _traceback):
        trace     = ''.join(traceback.format_tb(_traceback))
        data      = f"Exectype:  {exctype}  <-->  Value:  {value}\n\n{trace}\n\n\n\n"
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
        id = widget.get_active_id()
        self.arc_command_buffer.set_text(self.arc_commands[int(id)])




    def do_action_from_menu_controls(self, widget, eventbutton):
        action        = widget.get_name()
        self.ctrlDown = True
        self.hide_context_menu()
        self.hide_new_file_menu()
        self.hide_edit_file_menu()

        if action == "open":
            self.open_files()
        if action == "open_with":
            self.show_appchooser_menu()
        if action == "execute":
            self.execute_files()
        if action == "execute_in_terminal":
            self.execute_files(in_terminal=True)
        if action == "rename":
            self.rename_files()
        if action == "cut":
            self.to_copy_files.clear()
            self.cut_files()
        if action == "copy":
            self.to_cut_files.clear()
            self.copy_files()
        if action == "paste":
            self.paste_files()
        if action == "archive":
            self.show_archiver_dialogue()
        if action == "delete":
            self.delete_files()
        if action == "trash":
            self.trash_files()
        if action == "go_to_trash":
            self.builder.get_object("path_entry").set_text(self.trash_files_path)


        if action == "create":
            self.create_file()
            self.hide_new_file_menu()

        self.ctrlDown = False


    def generate_windows(self, data = None):
        if data:
            for j, value in enumerate(data):
                i = j + 1
                isHidden = True if value[0]["window"]["isHidden"] == "True" else False
                object   = self.builder.get_object(f"tggl_notebook_{i}")
                views    = value[0]["window"]["views"]
                self.window_controller.create_window()
                object.set_active(True)

                for view in views:
                    self.create_new_view_notebook(None, i, view)

                if isHidden:
                    self.toggle_notebook_pane(object)
        else:
            for j in range(0, 4):
                i = j + 1
                self.window_controller.create_window()
                self.create_new_view_notebook(None, i, None)
