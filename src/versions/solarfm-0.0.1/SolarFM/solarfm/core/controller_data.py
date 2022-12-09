# Python imports
import sys
import os
import signal
import subprocess
from dataclasses import dataclass

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GLib

# Application imports
from shellfm.windows.controller import WindowController
from plugins.plugins_controller import PluginsController




@dataclass(slots=True)
class State:
    fm_controller: any = None
    notebooks: any     = None
    wid: int  = None
    tid: int  = None
    tab: type = None
    icon_grid: gi.overrides.Gtk.IconView = None
    store: gi.overrides.Gtk.ListStore    = None
    uris:           []   = None
    uris_raw:       []   = None
    selected_files: []   = None
    to_copy_files:  []   = None
    to_cut_files:   []   = None
    message_dialog: type = None


class Controller_Data:
    """ Controller_Data contains most of the state of the app at ay given time. It also has some support methods. """
    __slots__ = "settings", "builder", "logger", "keybindings", "trashman", "fm_controller", "window", "window1", "window2", "window3", "window4"

    def setup_controller_data(self) -> None:
        self.builder            = settings.get_builder()
        self.keybindings        = settings.get_keybindings()

        self.fm_controller      = WindowController()
        self.plugins            = PluginsController()
        self.fm_controller_data = self.fm_controller.get_state_from_file()

        self.window             = settings.get_main_window()
        self.window1            = self.builder.get_object("window_1")
        self.window2            = self.builder.get_object("window_2")
        self.window3            = self.builder.get_object("window_3")
        self.window4            = self.builder.get_object("window_4")

        self.path_entry              = self.builder.get_object("path_entry")
        self.bottom_size_label       = self.builder.get_object("bottom_size_label")
        self.bottom_file_count_label = self.builder.get_object("bottom_file_count_label")
        self.bottom_path_label       = self.builder.get_object("bottom_path_label")

        self.notebooks          = [self.window1, self.window2, self.window3, self.window4]
        self.selected_files     = []
        self.to_copy_files      = []
        self.to_cut_files       = []
        self.soft_update_lock   = {}
        self.dnd_left_primed    = 0

        self.single_click_open  = False
        self.is_pane1_hidden    = False
        self.is_pane2_hidden    = False
        self.is_pane3_hidden    = False
        self.is_pane4_hidden    = False

        self.override_drop_dest = None
        self.ctrl_down          = False
        self.shift_down         = False
        self.alt_down           = False

        # sys.excepthook = self.custom_except_hook
        self.window.connect("delete-event", self.tear_down)
        GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, self.tear_down)

        self.window.show()
        if settings.is_debug():
            self.window.set_interactive_debugging(True)


    def get_current_state(self) -> State:
        '''
        Returns the state info most useful for any given context and action intent.

                Parameters:
                        a (obj): self

                Returns:
                        state (obj): State
        '''
        state                = State()
        state.fm_controller  = self.fm_controller
        state.notebooks      = self.notebooks
        state.wid, state.tid = self.fm_controller.get_active_wid_and_tid()
        state.tab            = self.get_fm_window(state.wid).get_tab_by_id(state.tid)
        state.icon_grid      = self.builder.get_object(f"{state.wid}|{state.tid}|icon_grid")
        state.store          = state.icon_grid.get_model()
        state.message_dialog = self.message_dialog

        selected_files       = state.icon_grid.get_selected_items()
        if selected_files:
            state.uris     = self.format_to_uris(state.store, state.wid, state.tid, selected_files, True)
            state.uris_raw = self.format_to_uris(state.store, state.wid, state.tid, selected_files)

        state.selected_files = event_system.emit_and_await("get_selected_files")

        # if self.to_copy_files:
        #     state.to_copy_files  = self.format_to_uris(state.store, state.wid, state.tid, self.to_copy_files, True)
        #
        # if self.to_cut_files:
        #     state.to_cut_files   = self.format_to_uris(state.store, state.wid, state.tid, self.to_cut_files, True)

        event_system.emit("update_state_info_plugins", state)
        return state


    def clear_console(self) -> None:
        ''' Clears the terminal screen. '''
        os.system('cls' if os.name == 'nt' else 'clear')

    def call_method(self, _method_name: str, data: type = None) -> type:
        '''
        Calls a method from scope of class.

                Parameters:
                        a (obj): self
                        b (str): method name to be called
                        c (*): Data (if any) to be passed to the method.
                                Note: It must be structured according to the given methods requirements.

                Returns:
                        Return data is that which the calling method gives.
        '''
        method_name = str(_method_name)
        method      = getattr(self, method_name, lambda data: f"No valid key passed...\nkey={method_name}\nargs={data}")
        return method(data) if data else method()

    def has_method(self, obj, name) -> type:
        ''' Checks if a given method exists. '''
        return callable(getattr(obj, name, None))


    def clear_notebooks(self) -> None:
        self.ctrl_down  = False
        self.shift_down = False
        self.alt_down   = False

        for notebook in self.notebooks:
            self.clear_children(notebook)

    def clear_children(self, widget: type) -> None:
        ''' Clear children of a gtk widget. '''
        for child in widget.get_children():
            widget.remove(child)

    def get_clipboard_data(self) -> str:
        proc    = subprocess.Popen(['xclip','-selection', 'clipboard', '-o'], stdout=subprocess.PIPE)
        retcode = proc.wait()
        data    = proc.stdout.read()
        return data.decode("utf-8").strip()

    def set_clipboard_data(self, data: type) -> None:
        proc = subprocess.Popen(['xclip','-selection','clipboard'], stdin=subprocess.PIPE)
        proc.stdin.write(data.encode("utf-8"))
        proc.stdin.close()
        retcode = proc.wait()
