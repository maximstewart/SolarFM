# Python imports
import os, gc, threading, time

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

# Application imports
from .mixins.exception_hook_mixin import ExceptionHookMixin
from .mixins.ui_mixin import UIMixin
from .signals.ipc_signals_mixin import IPCSignalsMixin
from .signals.keyboard_signals_mixin import KeyboardSignalsMixin
from .controller_data import Controller_Data


# NOTE: Threads will not die with parent's destruction
def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs, daemon=False).start()
    return wrapper

# NOTE: Insure threads die with parent's destruction
def daemon_threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs, daemon=True).start()
    return wrapper




class Controller(UIMixin, KeyboardSignalsMixin, IPCSignalsMixin, ExceptionHookMixin, Controller_Data):
    """ Controller coordinates the mixins and is somewhat the root hub of it all. """
    def __init__(self, args, unknownargs, _settings):
        self.setup_controller_data(_settings)
        self.window.show()

        self.generate_windows(self.fm_controller_data)
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
        self.fm_controller.save_state()
        time.sleep(event_sleep_time)
        Gtk.main_quit()


    @daemon_threaded
    def gui_event_observer(self):
        while True:
            time.sleep(event_sleep_time)
            event = event_system.consume_gui_event()
            if event:
                try:
                    sender_id, method_target, parameters = event
                    if sender_id:
                        method = getattr(self.__class__, "handle_gui_event_and_return_message")
                        GLib.idle_add(method, *(self, sender_id, method_target, parameters))
                    else:
                        method = getattr(self.__class__, method_target)
                        GLib.idle_add(method, *(self, *parameters,))
                except Exception as e:
                    print(repr(e))

    def handle_gui_event_and_return_message(self, sender, method_target, parameters):
        method = getattr(self.__class__, f"{method_target}")
        data   = method(*(self, *parameters))
        event_system.push_module_event([sender, None, data])

    def handle_plugin_key_event(self, sender, method_target, parameters=()):
        event_system.push_module_event([sender, method_target, parameters])


    def save_load_session(self, action="save_session"):
        wid, tid          = self.fm_controller.get_active_wid_and_tid()
        tab               = self.get_fm_window(wid).get_tab_by_id(tid)
        save_load_dialog  = self.builder.get_object("save_load_dialog")

        if action == "save_session":
            self.fm_controller.save_state()
            return
        elif action == "save_session_as":
            save_load_dialog.set_action(Gtk.FileChooserAction.SAVE)
        elif action == "load_session":
            save_load_dialog.set_action(Gtk.FileChooserAction.OPEN)
        else:
            raise Exception(f"Unknown action given:  {action}")

        save_load_dialog.set_current_folder(tab.get_current_directory())
        save_load_dialog.set_current_name("session.json")
        response = save_load_dialog.run()
        if response == Gtk.ResponseType.OK:
            if action == "save_session_as":
                path = f"{save_load_dialog.get_current_folder()}/{save_load_dialog.get_current_name()}"
                self.fm_controller.save_state(path)
            elif action == "load_session":
                path         = f"{save_load_dialog.get_file().get_path()}"
                session_json = self.fm_controller.get_state_from_file(path)
                self.load_session(session_json)
        if (response == Gtk.ResponseType.CANCEL) or (response == Gtk.ResponseType.DELETE_EVENT):
            pass

        save_load_dialog.hide()

    def load_session(self, session_json):
        if debug:
            self.logger.debug(f"Session Data: {session_json}")

        self.ctrl_down  = False
        self.shift_down = False
        self.alt_down   = False
        for notebook in self.notebooks:
            self.clear_children(notebook)

        self.fm_controller.unload_tabs_and_windows()
        self.generate_windows(session_json)
        gc.collect()


    def do_action_from_menu_controls(self, widget, event_button):
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
            self.cut_files()
        if action == "copy":
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






    def go_home(self, widget=None, eve=None):
        self.builder.get_object("go_home").released()

    def refresh_tab(self, widget=None, eve=None):
        self.builder.get_object("refresh_tab").released()

    def go_up(self, widget=None, eve=None):
        self.builder.get_object("go_up").released()

    def grab_focus_path_entry(self, widget=None, eve=None):
        self.builder.get_object("path_entry").grab_focus()

    def tggl_top_main_menubar(self, widget=None, eve=None):
        top_main_menubar = self.builder.get_object("top_main_menubar")
        top_main_menubar.hide() if top_main_menubar.is_visible() else top_main_menubar.show()

    def open_terminal(self, widget=None, eve=None):
        wid, tid = self.fm_controller.get_active_wid_and_tid()
        tab      = self.get_fm_window(wid).get_tab_by_id(tid)
        tab.execute([f"{tab.terminal_app}"], start_dir=tab.get_current_directory())
