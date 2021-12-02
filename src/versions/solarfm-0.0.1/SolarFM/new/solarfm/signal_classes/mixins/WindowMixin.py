# Python imports
import copy
from os.path import isdir, isfile


# Gtk imports
import gi
from gi.repository import Gdk

# Application imports
from . import TabMixin
from . import WidgetMixin



class WindowMixin(TabMixin):
    """docstring for WindowMixin"""
    def get_fm_window(self, wid):
        return self.window_controller.get_window_by_nickname(f"window_{wid}")

    def format_to_uris(self, store, wid, tid, treePaths, use_just_path=False):
        view = self.get_fm_window(wid).get_view_by_id(tid)
        dir  = view.get_current_directory()
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


    def set_bottom_labels(self, view):
        self.bottom_size_label.set_label("TBD")
        if view.hide_hidden:
            if view.get_hidden_count() > 0:
                self.bottom_file_count_label.set_label(f"{view.get_not_hidden_count()} visible ({view.get_hidden_count()} hidden)")
            else:
                self.bottom_file_count_label.set_label(f"{view.get_files_count()} items")
        else:
            self.bottom_file_count_label.set_label(f"{view.get_files_count()} items")
        self.bottom_path_label.set_label(view.get_current_directory())


    def set_window_title(self):
        wid, tid = self.window_controller.get_active_data()
        notebook = self.builder.get_object(f"window_{wid}")
        view     = self.get_fm_window(wid).get_view_by_id(tid)
        dir      = view.get_current_directory()

        for _notebook in self.notebooks:
            ctx      = _notebook.get_style_context()
            ctx.remove_class("notebook-selected-focus")

        ctx      = notebook.get_style_context()
        ctx.add_class("notebook-selected-focus")

        self.window.set_title("SolarFM ~ " + dir)
        self.set_bottom_labels(view)

    def set_path_text(self, wid, tid):
        path_entry = self.builder.get_object("path_entry")
        view       = self.get_fm_window(wid).get_view_by_id(tid)
        path_entry.set_text(view.get_current_directory())

    def grid_set_selected_items(self, iconview):
        self.selected_files = iconview.get_selected_items()

    def grid_icon_single_left_click(self, iconview, eve):
        try:
            wid, tid = iconview.get_name().split("|")
            self.window_controller.set_active_data(wid, tid)
            self.set_path_text(wid, tid)
            self.set_window_title()

            if eve.type == Gdk.EventType.BUTTON_RELEASE and eve.button == 1:   # l-click
                if self.single_click_open: # FIXME: need to find a way to pass the model index
                    self.grid_icon_double_left_click(iconview)
            elif eve.type == Gdk.EventType.BUTTON_RELEASE and eve.button == 3: # r-click
                self.show_context_menu()

        except Exception as e:
            print(repr(e))
            self.display_message(self.error, f"{repr(e)}")

    def grid_icon_double_left_click(self, iconview, item, data=None):
        try:
            if self.ctrlDown and self.shiftDown:
                self.execute_files(in_terminal=True)
                return
            elif self.ctrlDown:
                self.execute_files()
                return

            wid, tid   = self.window_controller.get_active_data()
            notebook   = self.builder.get_object(f"window_{wid}")
            path_entry = self.builder.get_object(f"path_entry")
            tab_label  = self.get_tab_label(notebook, iconview)

            view       = self.get_fm_window(wid).get_view_by_id(tid)
            model      = iconview.get_model()

            fileName   = model[item][1]
            dir        = view.get_current_directory()
            file       = dir + "/" + fileName

            if isdir(file):
                view.set_path(file)
                self.load_store(view, model)
                tab_label.set_label(view.get_end_of_path())
                path_entry.set_text(view.get_current_directory())
                self.set_file_watcher(view)
                self.set_bottom_labels(view)
            else:
                view.open_file_locally(file)
        except Exception as e:
            self.display_message(self.error, f"{repr(e)}")



    def grid_on_drag_set(self, iconview, drag_context, data, info, time):
        action    = iconview.get_name()
        wid, tid  = action.split("|")
        store     = iconview.get_model()
        treePaths = iconview.get_selected_items()
        uris      = self.format_to_uris(store, wid, tid, treePaths)

        data.set_uris(uris)

    def grid_on_drag_motion(self, iconview, drag_context, x, y, data):
        wid, tid = iconview.get_name().split("|")
        self.window_controller.set_active_data(wid, tid)

    def grid_on_drag_data_received(self, widget, drag_context, x, y, data, info, time):
        if info == 80:
            wid, tid  = self.window_controller.get_active_data()
            notebook  = self.builder.get_object(f"window_{wid}")
            store, tab_label = self.get_store_and_label_from_notebook(notebook, f"{wid}|{tid}")
            view      = self.get_fm_window(wid).get_view_by_id(tid)

            uris  = data.get_uris()
            dest  = f"file://{view.get_current_directory()}"

            if len(uris) > 0:
                self.move_files(uris, dest)


    def create_new_view_notebook(self, widget=None, wid=None, path=None):
        self.create_tab(wid, path)
