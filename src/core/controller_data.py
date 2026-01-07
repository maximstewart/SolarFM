# Python imports
import os
import subprocess

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Application imports
from .sfm_builder import SFMBuilder
from .widgets.dialogs.message_widget import MessageWidget
from .widgets.dialogs.user_pass_widget import UserPassWidget

from utils.types.state import State
from plugins.plugins_controller import PluginsController
from shellfm.windows.controller import WindowController



class Controller_Data:
    """ Controller_Data contains most of the state of the app at ay given time. It also has some support methods. """
    __slots__ = "settings", "builder", "logger", "keybindings", "trashman", "fm_controller", "window", "window1", "window2", "window3", "window4"

    def _setup_controller_data(self) -> None:
        self.window        = settings_manager.get_main_window()
        self.builder       = SFMBuilder()
        self.core_widget   = None

        self._load_glade_file()
        self.fm_controller      = WindowController()
        self.plugins_controller = PluginsController()
        self.fm_controller_data = self.fm_controller.get_state_from_file()

        self.window1            = self.builder.get_object("window_1")
        self.window2            = self.builder.get_object("window_2")
        self.window3            = self.builder.get_object("window_3")
        self.window4            = self.builder.get_object("window_4")

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
        self.was_midified_key   = None

        self._state           = State()
        self.message_dialog   = MessageWidget()
        self.user_pass_dialog = UserPassWidget()


    def get_current_state(self) -> State:
        '''
        Returns the state info most useful for any given context and action intent.

                Parameters:
                        a (obj): self

                Returns:
                        state (obj): State
        '''

        state                  = self._state
        state.fm_controller    = self.fm_controller
        state.notebooks        = self.notebooks
        state.wid, state.tid   = self.fm_controller.get_active_wid_and_tid()
        state.tab              = self.get_fm_window(state.wid).get_tab_by_id(state.tid)
        state.icon_grid        = self.builder.get_object(f"{state.wid}|{state.tid}|icon_grid", use_gtk = False)
        state.store            = state.icon_grid.get_model()
        state.message_dialog   = self.message_dialog
        state.user_pass_dialog = self.user_pass_dialog

        selected_files     = state.icon_grid.get_selected_items()
        if selected_files:
            state.uris     = self.format_to_uris(state.store, state.wid, state.tid, selected_files, True)
            state.uris_raw = self.format_to_uris(state.store, state.wid, state.tid, selected_files)

        state.selected_files = event_system.emit_and_await("get_selected_files")

        event_system.emit("update_state_info_plugins", state) # NOTE: Need to remove after we convert plugins to use emit_and_await
        return state

    def format_to_uris(self, store, wid, tid, treePaths, use_just_path = False):
        tab  = self.get_fm_window(wid).get_tab_by_id(tid)
        dir  = tab.get_current_directory()
        uris = []

        for path in treePaths:
            itr   = store.get_iter(path)
            file  = store.get(itr, 1)[0]
            fpath = ""

            if not use_just_path:
                fpath = f"file://{dir}/{file}"
            else:
                fpath = f"{dir}/{file}"

            uris.append(fpath)

        tab = None
        dir = None

        return uris


    def get_fm_window(self, wid):
        return self.fm_controller.get_window_by_nickname(f"window_{wid}")

    def _unset_selected_files_views(self):
        for _notebook in self.notebooks:
            ctx = _notebook.get_style_context()
            ctx.remove_class("notebook-selected-focus")
            ctx.add_class("notebook-unselected-focus")

    def _set_window_title(self, dir):
        self.window.set_title(f"{app_name} ~ {dir}")


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
