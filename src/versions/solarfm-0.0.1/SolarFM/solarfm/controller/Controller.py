# Python imports
import traceback, threading, inspect, os, gc, time

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

# Application imports
from .mixins import ExceptionHookMixin, UIMixin
from .signals import IPCSignalsMixin, KeyboardSignalsMixin
from . import Controller_Data


def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs, daemon=True).start()
    return wrapper




class Controller(UIMixin, KeyboardSignalsMixin, IPCSignalsMixin, ExceptionHookMixin, Controller_Data):
    ''' Controller coordinates the mixins and is somewhat the root hub of it all. '''
    def __init__(self, args, unknownargs, _settings):
        self.setup_controller_data(_settings)
        self.window.show()

        self.generate_windows(self.state)
        self.plugins.launch_plugins()

        if debug:
            self.window.set_interactive_debugging(True)

        if not trace_debug:
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
        event_system.send_ipc_message("close server")
        self.window_controller.save_state()
        time.sleep(event_sleep_time)
        Gtk.main_quit()


    @threaded
    def gui_event_observer(self):
        while True:
            time.sleep(event_sleep_time)
            event = event_system.consume_gui_event()
            if event:
                try:
                    type, target, data = event
                    if type:
                        method = getattr(self.__class__, "handle_gui_event_and_set_message")
                        GLib.idle_add(method, *(self, type, target, data))
                    else:
                        method = getattr(self.__class__, target)
                        GLib.idle_add(method, *(self, *data,))
                except Exception as e:
                    print(repr(e))

    def handle_gui_event_and_set_message(self, type, target, parameters):
        method = getattr(self.__class__, f"{target}")
        data   = method(*(self, *parameters))
        self.plugins.set_message_on_plugin(type, data)

    def open_terminal(self, widget=None, eve=None):
        wid, tid = self.window_controller.get_active_wid_and_tid()
        view     = self.get_fm_window(wid).get_view_by_id(tid)
        dir      = view.get_current_directory()
        view.execute(f"{view.terminal_app}", dir)

    def save_load_session(self, action="save_session"):
        wid, tid          = self.window_controller.get_active_wid_and_tid()
        view              = self.get_fm_window(wid).get_view_by_id(tid)
        save_load_dialog  = self.builder.get_object("save_load_dialog")

        if action == "save_session":
            self.window_controller.save_state()
            return
        elif action == "save_session_as":
            save_load_dialog.set_action(Gtk.FileChooserAction.SAVE)
        elif action == "load_session":
            save_load_dialog.set_action(Gtk.FileChooserAction.OPEN)
        else:
            raise Exception(f"Unknown action given:  {action}")

        save_load_dialog.set_current_folder(view.get_current_directory())
        save_load_dialog.set_current_name("session.json")
        response = save_load_dialog.run()
        if response == Gtk.ResponseType.OK:
            if action == "save_session":
                path = f"{save_load_dialog.get_current_folder()}/{save_load_dialog.get_current_name()}"
                self.window_controller.save_state(path)
            elif action == "load_session":
                path         = f"{save_load_dialog.get_file().get_path()}"
                session_json = self.window_controller.load_state(path)
                self.load_session(session_json)
        if (response == Gtk.ResponseType.CANCEL) or (response == Gtk.ResponseType.DELETE_EVENT):
            pass

        save_load_dialog.hide()

    def load_session(self, session_json):
        if debug:
            print(f"Session Data: {session_json}")

        self.ctrlDown          = False
        self.shiftDown         = False
        self.altDown           = False
        for notebook in self.notebooks:
            self.clear_children(notebook)

        self.window_controller.unload_views_and_windows()
        self.generate_windows(session_json)
        gc.collect()


    def do_action_from_menu_controls(self, widget, eventbutton):
        action = widget.get_name()
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
            self.path_entry.set_text(self.trash_files_path)
        if action == "restore_from_trash":
            self.restore_trash_files()
        if action == "empty_trash":
            self.empty_trash()

        if action == "create":
            self.show_new_file_menu()
        if action in ["save_session", "save_session_as", "load_session"]:
            self.save_load_session(action)
