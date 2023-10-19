# Python imports
import copy
import traceback
from os.path import isdir

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Gio

# Application imports
from .tab_mixin import TabMixin


class WindowException(Exception):
    ...


class WindowMixin(TabMixin):
    """docstring for WindowMixin"""

    def get_fm_window(self, wid):
        return self.fm_controller.get_window_by_nickname(f"window_{wid}")

    def set_bottom_labels(self, tab):
        event_system.emit("set_bottom_labels", (tab,))

    def set_window_title(self):
        wid, tid = self.fm_controller.get_active_wid_and_tid()
        notebook = self.builder.get_object(f"window_{wid}")
        tab      = self.get_fm_window(wid).get_tab_by_id(tid)
        dir      = tab.get_current_directory()

        event_system.emit("unset_selected_files_views")
        ctx = self.files_view.get_style_context()
        ctx.remove_class("notebook-unselected-focus")
        ctx.add_class("notebook-selected-focus")

        event_system.emit("set_window_title", (dir,))
        self.set_bottom_labels(tab)

    def set_path_text(self, wid, tid):
        tab = self.get_fm_window(wid).get_tab_by_id(tid)
        event_system.emit("go_to_path", (tab.get_current_directory(),))

    def grid_set_selected_items(self, icons_grid):
        new_items      = icons_grid.get_selected_items()
        items_size     = len(new_items)
        selected_items = event_system.emit_and_await("get_selected_files")

        if items_size == 1:
            # NOTE: If already in selection, likely dnd else not so wont readd
            if new_items[0] in selected_items:
                self.dnd_left_primed += 1
                # NOTE: If in selection but trying to just select an already selected item.
                if self.dnd_left_primed > 1:
                    self.dnd_left_primed = 0
                    selected_items.clear()

                # NOTE: Likely trying dnd, just readd to selection the former set.
                #       Prevents losing highlighting of grid selected.
                for path in selected_items:
                    icons_grid.select_path(path)

        if items_size > 0:
            event_system.emit("set_selected_files", (new_items,))
        else:
            self.dnd_left_primed = 0
            selected_items.clear()

    def grid_icon_single_click(self, icons_grid, eve):
        try:
            event_system.emit("hide_path_menu")
            wid, tid = icons_grid.get_name().split("|")
            self.fm_controller.set_wid_and_tid(wid, tid)
            self.set_path_text(wid, tid)
            self.set_window_title()

            if eve.type == Gdk.EventType.BUTTON_RELEASE and eve.button == 1:   # l-click
                if eve.state & Gdk.ModifierType.CONTROL_MASK:
                    self.dnd_left_primed = 0

                if self.single_click_open: # FIXME: need to find a way to pass the model index
                    self.grid_icon_double_click(icons_grid)
            elif eve.type == Gdk.EventType.BUTTON_RELEASE and eve.button == 3: # r-click
                event_system.emit("show_context_menu")

        except WindowException as e:
            logger.info(repr(e))
            self.display_message(settings.theming.error_color, f"{repr(e)}")

    def grid_icon_double_click(self, icons_grid, item, data=None):
        try:
            if self.ctrl_down and self.shift_down:
                self.unset_keys_and_data()
                self.execute_files(in_terminal=True)
                return
            elif self.ctrl_down:
                self.unset_keys_and_data()
                self.execute_files()
                return


            state      = self.get_current_state()
            notebook   = self.builder.get_object(f"window_{state.wid}")
            tab_label  = self.get_tab_label(notebook, state.icon_grid)

            fileName   = state.store[item][1]
            dir        = state.tab.get_current_directory()
            file       = f"{dir}/{fileName}"

            if isdir(file):
                state.tab.set_path(file)
                state.icon_grid.clear_and_set_new_store()
                self.update_tab(tab_label, state.tab, state.icon_grid.get_store(), state.wid, state.tid)
            else:
                event_system.emit("open_files")
        except WindowException as e:
            traceback.print_exc()
            self.display_message(settings.theming.error_color, f"{repr(e)}")



    def grid_on_drag_set(self, icons_grid, drag_context, data, info, time):
        action    = icons_grid.get_name()
        wid, tid  = action.split("|")
        store     = icons_grid.get_model()
        treePaths = icons_grid.get_selected_items()
        # NOTE: Need URIs as URI format for DnD to work. Will strip 'file://'
        #       further down call chain when doing internal fm stuff.
        uris      = self.format_to_uris(store, wid, tid, treePaths)
        uris_text = '\n'.join(uris)

        data.set_uris(uris)
        data.set_text(uris_text, -1)

    def grid_on_drag_motion(self, icons_grid, drag_context, x, y, data):
        current     = '|'.join(self.fm_controller.get_active_wid_and_tid())
        target      = icons_grid.get_name()
        wid, tid    = target.split("|")
        store       = icons_grid.get_model()
        path_at_loc = None

        try:
            data = icons_grid.get_dest_item_at_pos(x, y)
            path_at_loc   = data[0]
            drop_position = data[1]
            highlighted_item_path = icons_grid.get_drag_dest_item().path
            if path_at_loc and path_at_loc == highlighted_item_path and drop_position == Gtk.IconViewDropPosition.DROP_INTO:
                uri = self.format_to_uris(store, wid, tid, highlighted_item_path)[0].replace("file://", "")
                self.override_drop_dest = uri if isdir(uri) else None
            else:
                self.override_drop_dest = None
        except Exception as e:
            self.override_drop_dest = None

        if target not in current:
            self.fm_controller.set_wid_and_tid(wid, tid)


    def grid_on_drag_data_received(self, widget, drag_context, x, y, data, info, time):
        if info == 80:
            uris  = data.get_uris()
            state = event_system.emit_and_await("get_current_state")
            dest  = f"{state.tab.get_current_directory()}" if not self.override_drop_dest else self.override_drop_dest
            if len(uris) == 0:
                uris = data.get_text().split("\n")

            from_uri = '/'.join(uris[0].replace("file://", "").split("/")[:-1])
            if from_uri != dest:
                event_system.emit("move_files", (uris, dest))


    def create_new_tab_notebook(self, widget=None, wid=None, path=None):
        self.create_tab(wid, None, path)
