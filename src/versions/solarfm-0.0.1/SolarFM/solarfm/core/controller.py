# Python imports
import os
import gc
import time

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GLib

# Application imports
from .controller_data import Controller_Data
from .mixins.signals_mixins import SignalsMixins
from .ui import UI




class Controller(UI, SignalsMixins, Controller_Data):
    """ Controller coordinates the mixins and is somewhat the root hub of it all. """
    def __init__(self, args, unknownargs):
        self._subscribe_to_events()
        self.setup_controller_data()
        self.generate_windows(self.fm_controller_data)

        if args.no_plugins == "false":
            self.plugins.launch_plugins()

        for arg in unknownargs + [args.new_tab,]:
            if os.path.isdir(arg):
                message = f"FILE|{arg}"
                event_system.emit("post_file_to_ipc", message)


    def _subscribe_to_events(self):
        event_system.subscribe("handle_file_from_ipc", self.handle_file_from_ipc)
        event_system.subscribe("get_current_state", self.get_current_state)
        event_system.subscribe("display_message", self.display_message)
        event_system.subscribe("go_to_path", self.go_to_path)
        event_system.subscribe("do_hide_context_menu", self.do_hide_context_menu)
        event_system.subscribe("do_action_from_menu_controls", self.do_action_from_menu_controls)

    def tear_down(self, widget=None, eve=None):
        if not settings.is_trace_debug():
            self.fm_controller.save_state()

        settings.clear_pid()
        time.sleep(event_sleep_time)
        Gtk.main_quit()


    def save_load_session(self, action="save_session"):
        wid, tid          = self.fm_controller.get_active_wid_and_tid()
        tab               = self.get_fm_window(wid).get_tab_by_id(tid)
        save_load_dialog  = self.builder.get_object("save_load_dialog")

        if action == "save_session":
            if not settings.is_trace_debug():
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
            ...

        save_load_dialog.hide()

    def load_session(self, session_json):
        if settings.is_debug():
            logger.debug(f"Session Data: {session_json}")

        self.ctrl_down  = False
        self.shift_down = False
        self.alt_down   = False
        for notebook in self.notebooks:
            self.clear_children(notebook)

        self.fm_controller.unload_tabs_and_windows()
        self.generate_windows(session_json)
        gc.collect()


    def do_action_from_menu_controls(self, widget, eve = None):
        if not isinstance(widget, str):
            action = widget.get_name()
        else:
            action = widget

        self.hide_context_menu()
        self.hide_new_file_menu()
        event_system.emit("do_hide_edit_file_menu")

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
        if action == "copy_name":
            self.copy_name()
        if action == "paste":
            self.paste_files()
        if action == "create":
            self.create_files()
        if action in ["save_session", "save_session_as", "load_session"]:
            self.save_load_session(action)


    @endpoint_registry.register(rule="go_home")
    def go_home(self, widget=None, eve=None):
        self.builder.get_object("go_home").released()

    @endpoint_registry.register(rule="refresh_tab")
    def refresh_tab(self, widget=None, eve=None):
        self.builder.get_object("refresh_tab").released()

    @endpoint_registry.register(rule="go_up")
    def go_up(self, widget=None, eve=None):
        self.builder.get_object("go_up").released()

    @endpoint_registry.register(rule="grab_focus_path_entry")
    def grab_focus_path_entry(self, widget=None, eve=None):
        self.builder.get_object("path_entry").grab_focus()

    @endpoint_registry.register(rule="tggl_top_main_menubar")
    def tggl_top_main_menubar(self, widget=None, eve=None):
        top_main_menubar = self.builder.get_object("top_main_menubar")
        top_main_menubar.hide() if top_main_menubar.is_visible() else top_main_menubar.show()

    @endpoint_registry.register(rule="open_terminal")
    def open_terminal(self, widget=None, eve=None):
        wid, tid = self.fm_controller.get_active_wid_and_tid()
        tab      = self.get_fm_window(wid).get_tab_by_id(tid)
        tab.execute([f"{tab.terminal_app}"], start_dir=tab.get_current_directory())

    def go_to_path(self, path):
        self.path_entry.set_text(path)

    def do_hide_context_menu(self):
        self.hide_context_menu()
