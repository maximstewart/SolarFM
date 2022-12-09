# Python imports
import os
import time

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GLib

# Application imports
from .controller_data import Controller_Data
from .fs_actions.file_system_actions import FileSystemActions
from .mixins.signals_mixins import SignalsMixins

from .widgets.dialogs.about_widget import AboutWidget
from .widgets.dialogs.appchooser_widget import AppchooserWidget
from .widgets.dialogs.file_exists_widget import FileExistsWidget
from .widgets.dialogs.new_file_widget import NewFileWidget
from .widgets.dialogs.message_widget import MessageWidget
from .widgets.dialogs.rename_widget import RenameWidget
from .widgets.dialogs.save_load_widget import SaveLoadWidget

from .widgets.popups.message_popup_widget import MessagePopupWidget
from .widgets.popups.path_menu_popup_widget import PathMenuPopupWidget
from .widgets.popups.plugins_popup_widget import PluginsPopupWidget
from .widgets.popups.io_popup_widget import IOPopupWidget

from .widgets.context_menu_widget import ContextMenuWidget

from .ui_mixin import UIMixin




class Controller(UIMixin, SignalsMixins, Controller_Data):
    """ Controller coordinates the mixins and is somewhat the root hub of it all. """

    def __init__(self, args, unknownargs):
        self._setup_styling()
        self._setup_signals()
        self._subscribe_to_events()
        self._load_widgets()

        self.setup_controller_data()
        self.generate_windows(self.fm_controller_data)

        if args.no_plugins == "false":
            self.plugins.launch_plugins()

        for arg in unknownargs + [args.new_tab,]:
            if os.path.isdir(arg):
                message = f"FILE|{arg}"
                event_system.emit("post_file_to_ipc", message)


    def _setup_styling(self):
        ...

    def _setup_signals(self):
        FileSystemActions()

    def _subscribe_to_events(self):
        event_system.subscribe("handle_file_from_ipc", self.handle_file_from_ipc)
        event_system.subscribe("generate_windows", self.generate_windows)
        event_system.subscribe("clear_notebooks", self.clear_notebooks)
        event_system.subscribe("get_current_state", self.get_current_state)
        event_system.subscribe("go_to_path", self.go_to_path)
        event_system.subscribe("do_action_from_menu_controls", self.do_action_from_menu_controls)
        event_system.subscribe("set_clipboard_data", self.set_clipboard_data)

    # NOTE: Really we will move these to the UI/(New) Window 'base' controller
    #       after we're done cleaning and refactoring to use fewer mixins.
    def _load_widgets(self):
        IOPopupWidget()
        MessagePopupWidget()
        PathMenuPopupWidget()
        PluginsPopupWidget()

        AboutWidget()
        AppchooserWidget()
        ContextMenuWidget()
        NewFileWidget()
        RenameWidget()
        FileExistsWidget()
        SaveLoadWidget()
        self.message_dialog = MessageWidget()


    def tear_down(self, widget=None, eve=None):
        if not settings.is_trace_debug():
            self.fm_controller.save_state()

        settings.clear_pid()
        time.sleep(event_sleep_time)
        Gtk.main_quit()

    def reload_plugins(self, widget=None, eve=None):
        self.plugins.reload_plugins()


    def do_action_from_menu_controls(self, _action=None, eve=None):
        if not _action:
            return

        if not isinstance(_action, str):
            action = _action.get_name()
        else:
            action = _action

        event_system.emit("hide_context_menu")
        event_system.emit("hide_new_file_menu")
        event_system.emit("hide_rename_file_menu")

        if action == "open":
            event_system.emit("open_files")
        if action == "open_with":
            event_system.emit("show_appchooser_menu")
        if action == "execute":
            event_system.emit("execute_files")
        if action == "execute_in_terminal":
            event_system.emit("execute_files", (True,))
        if action == "rename":
            event_system.emit("rename_files")
        if action == "cut":
            event_system.emit("cut_files")
        if action == "copy":
            event_system.emit("copy_files")
        if action == "copy_name":
            event_system.emit("copy_name")
        if action == "paste":
            event_system.emit("paste_files")
        if action == "create":
            event_system.emit("create_files")
        if action in ["save_session", "save_session_as", "load_session"]:
            event_system.emit("save_load_session", (action))

        if action == "about_page":
            event_system.emit("show_about_page")
        if action == "io_popup":
            event_system.emit("show_io_popup")
        if action == "plugins_popup":
            event_system.emit("show_plugins_popup")
        if action == "messages_popup":
            event_system.emit("show_messages_popup")


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

    def go_to_path(self, path: str):
        self.path_entry.set_text(path)
