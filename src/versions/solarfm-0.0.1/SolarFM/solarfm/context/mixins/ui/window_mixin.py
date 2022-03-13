# Python imports
import copy
from os.path import isdir, isfile


# Lib imports
import gi
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk, Gio

# Application imports
from .tab_mixin import TabMixin


class WindowMixin(TabMixin):
    """docstring for WindowMixin"""

    def generate_windows(self, session_json = None):
        if session_json:
            for j, value in enumerate(session_json):
                i = j + 1
                notebook_tggl_button = self.builder.get_object(f"tggl_notebook_{i}")
                is_hidden = True if value[0]["window"]["isHidden"] == "True" else False
                tabs      = value[0]["window"]["tabs"]
                self.fm_controller.create_window()
                notebook_tggl_button.set_active(True)

                if tabs:
                    for tab in tabs:
                        self.create_new_tab_notebook(None, i, tab)
                else:
                    self.create_new_tab_notebook(None, i, None)

                if is_hidden:
                    self.toggle_notebook_pane(notebook_tggl_button)

            try:
                if not self.is_pane4_hidden:
                    icon_grid = self.window4.get_children()[1].get_children()[0]
                elif not self.is_pane3_hidden:
                    icon_grid = self.window3.get_children()[1].get_children()[0]
                elif not self.is_pane2_hidden:
                    icon_grid = self.window2.get_children()[1].get_children()[0]
                elif not self.is_pane1_hidden:
                    icon_grid = self.window1.get_children()[1].get_children()[0]

                icon_grid.event(Gdk.Event().new(type=Gdk.EventType.BUTTON_RELEASE))
                icon_grid.event(Gdk.Event().new(type=Gdk.EventType.BUTTON_RELEASE))
            except Exception as e:
                print("\n:  The saved session might be missing window data!  :\nLocation: ~/.config/solarfm/session.json\nFix: Back it up and delete it to reset.\n")
                print(repr(e))
        else:
            for j in range(0, 4):
                i = j + 1
                self.fm_controller.create_window()
                self.create_new_tab_notebook(None, i, None)


    def get_fm_window(self, wid):
        return self.fm_controller.get_window_by_nickname(f"window_{wid}")

    def format_to_uris(self, store, wid, tid, treePaths, use_just_path=False):
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

        return uris


    def set_bottom_labels(self, tab):
        state                = self.get_current_state()
        selected_files       = state.icon_grid.get_selected_items()
        current_directory    = tab.get_current_directory()
        path_file            = Gio.File.new_for_path(current_directory)
        mount_file           = path_file.query_filesystem_info(attributes="filesystem::*", cancellable=None)
        formatted_mount_free = self.sizeof_fmt( int(mount_file.get_attribute_as_string("filesystem::free")) )
        formatted_mount_size = self.sizeof_fmt( int(mount_file.get_attribute_as_string("filesystem::size")) )

        if self.trash_files_path == current_directory:
            self.builder.get_object("restore_from_trash").show()
            self.builder.get_object("empty_trash").show()
        else:
            self.builder.get_object("restore_from_trash").hide()
            self.builder.get_object("empty_trash").hide()

        # If something selected
        self.bottom_size_label.set_label(f"{formatted_mount_free} free / {formatted_mount_size}")
        self.bottom_path_label.set_label(tab.get_current_directory())
        if selected_files:
            uris          = self.format_to_uris(state.store, state.wid, state.tid, selected_files, True)
            combined_size = 0
            for uri in uris:
                try:
                    file_info = Gio.File.new_for_path(uri).query_info(attributes="standard::size",
                                                        flags=Gio.FileQueryInfoFlags.NONE,
                                                        cancellable=None)
                    file_size = file_info.get_size()
                    combined_size += file_size
                except Exception as e:
                    if debug:
                        print(repr(e))


            formatted_size = self.sizeof_fmt(combined_size)
            if tab.is_hiding_hidden():
                self.bottom_path_label.set_label(f" {len(uris)} / {tab.get_files_count()} ({formatted_size})")
            else:
                self.bottom_path_label.set_label(f" {len(uris)} / {tab.get_not_hidden_count()} ({formatted_size})")

            return

        # If nothing selected
        if tab.is_hiding_hidden():
            if tab.get_hidden_count() > 0:
                self.bottom_file_count_label.set_label(f"{tab.get_not_hidden_count()} visible ({tab.get_hidden_count()} hidden)")
            else:
                self.bottom_file_count_label.set_label(f"{tab.get_files_count()} items")
        else:
            self.bottom_file_count_label.set_label(f"{tab.get_files_count()} items")



    def set_window_title(self):
        wid, tid = self.fm_controller.get_active_wid_and_tid()
        notebook = self.builder.get_object(f"window_{wid}")
        tab      = self.get_fm_window(wid).get_tab_by_id(tid)
        dir      = tab.get_current_directory()

        for _notebook in self.notebooks:
            ctx = _notebook.get_style_context()
            ctx.remove_class("notebook-selected-focus")
            ctx.add_class("notebook-unselected-focus")

        ctx = notebook.get_style_context()
        ctx.remove_class("notebook-unselected-focus")
        ctx.add_class("notebook-selected-focus")

        self.window.set_title(f"SolarFM ~ {dir}")
        self.set_bottom_labels(tab)

    def set_path_text(self, wid, tid):
        path_entry = self.builder.get_object("path_entry")
        tab        = self.get_fm_window(wid).get_tab_by_id(tid)
        path_entry.set_text(tab.get_current_directory())

    def grid_set_selected_items(self, icons_grid):
        self.selected_files = icons_grid.get_selected_items()

    def grid_cursor_toggled(self, icons_grid):
        print("wat...")

    def grid_icon_single_click(self, icons_grid, eve):
        try:
            self.path_menu.popdown()
            wid, tid = icons_grid.get_name().split("|")
            self.fm_controller.set_wid_and_tid(wid, tid)
            self.set_path_text(wid, tid)
            self.set_window_title()


            if eve.type == Gdk.EventType.BUTTON_RELEASE and eve.button == 1:   # l-click
                if self.single_click_open: # FIXME: need to find a way to pass the model index
                    self.grid_icon_double_click(icons_grid)
            elif eve.type == Gdk.EventType.BUTTON_RELEASE and eve.button == 3: # r-click
                self.show_context_menu()

        except Exception as e:
            print(repr(e))
            self.display_message(self.error_color, f"{repr(e)}")

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
            tab_label  = self.get_tab_label(notebook, icons_grid)

            fileName   = state.store[item][1]
            dir        = state.tab.get_current_directory()
            file       = f"{dir}/{fileName}"

            if isdir(file):
                state.tab.set_path(file)
                self.update_tab(tab_label, state.tab, state.store, state.wid, state.tid)
            else:
                self.open_files()
        except Exception as e:
            self.display_message(self.error_color, f"{repr(e)}")



    def grid_on_drag_set(self, icons_grid, drag_context, data, info, time):
        action    = icons_grid.get_name()
        wid, tid  = action.split("|")
        store     = icons_grid.get_model()
        treePaths = icons_grid.get_selected_items()
        # NOTE: Need URIs as URI format for DnD to work. Will strip 'file://'
        # further down call chain when doing internal fm stuff.
        uris      = self.format_to_uris(store, wid, tid, treePaths)
        uris_text = '\n'.join(uris)

        data.set_uris(uris)
        data.set_text(uris_text, -1)

    def grid_on_drag_motion(self, icons_grid, drag_context, x, y, data):
        current   = '|'.join(self.fm_controller.get_active_wid_and_tid())
        target    = icons_grid.get_name()
        wid, tid  = target.split("|")
        store     = icons_grid.get_model()
        treePath  = icons_grid.get_drag_dest_item().path

        if treePath:
            uri = self.format_to_uris(store, wid, tid, treePath)[0].replace("file://", "")
            self.override_drop_dest = uri if isdir(uri) else None

        if target not in current:
            self.fm_controller.set_wid_and_tid(wid, tid)


    def grid_on_drag_data_received(self, widget, drag_context, x, y, data, info, time):
        if info == 80:
            wid, tid  = self.fm_controller.get_active_wid_and_tid()
            notebook  = self.builder.get_object(f"window_{wid}")
            store, tab_label = self.get_store_and_label_from_notebook(notebook, f"{wid}|{tid}")
            tab       = self.get_fm_window(wid).get_tab_by_id(tid)

            uris = data.get_uris()
            dest = f"{tab.get_current_directory()}" if not self.override_drop_dest else self.override_drop_dest
            if len(uris) == 0:
                uris = data.get_text().split("\n")

            from_uri = '/'.join(uris[0].replace("file://", "").split("/")[:-1])
            if from_uri != dest:
                self.move_files(uris, dest)


    def create_new_tab_notebook(self, widget=None, wid=None, path=None):
        self.create_tab(wid, None, path)
