# Python imports
import copy
from os.path import isdir, isfile


# Lib imports
from . import TabMixin

import gi

from gi.repository import Gdk

# Application imports
from . import WidgetMixin



class WindowMixin(TabMixin):
    """docstring for WindowMixin"""
    def get_fm_window(self, wid):
        return self.window_controller.get_window_by_nickname(f"window_{wid}")

    def set_window_title(self):
        wid, tid = self.window_controller.get_active_data()
        view     = self.get_fm_window(wid).get_view_by_id(tid)
        dir      = view.get_current_directory()
        self.window.set_title(dir)

    def set_path_text(self, wid, tid):
        path_entry = self.builder.get_object("path_entry")
        view       = self.get_fm_window(wid).get_view_by_id(tid)
        path_entry.set_text(view.get_current_directory())

    def grid_icon_single_click(self, widget, eve):
        try:
            wid, tid = widget.get_name().split("|")
            self.window_controller.set_active_data(wid, tid)

            if eve.type == Gdk.EventType.BUTTON_RELEASE and eve.button == 1:   # l-click
                self.set_path_text(wid, tid)
                self.set_window_title()

                if self.single_click_open: # FIXME: need to find a way to pass the model index
                    self.grid_icon_double_left_click(widget)
            elif eve.type == Gdk.EventType.BUTTON_RELEASE and eve.button == 3: # r-click
                pass
            #     input          = self.builder.get_object("filenameInput")
            #     controls       = self.builder.get_object("iconControlsWindow")
            #     iconsButtonBox = self.builder.get_object("iconsButtonBox")
            #     menuButtonBox  = self.builder.get_object("menuButtonBox")
            #
            #
            #     if len(self.selectedFiles) == 1:
            #         parts = self.selectedFiles[0].split("/")
            #         input.set_text(parts[len(parts) - 1])
            #         input.show()
            #         iconsButtonBox.show()
            #         menuButtonBox.hide()
            #         controls.show()
            #     elif len(self.selectedFiles) > 1:
            #         input.set_text("")
            #         input.hide()
            #         menuButtonBox.hide()
            #         iconsButtonBox.show()
            #         controls.show()
            #     else:
            #         input.set_text("")
            #         input.show()
            #         menuButtonBox.show()
            #         iconsButtonBox.hide()
            #         controls.show()

        except Exception as e:
            print(repr(e))

    def grid_icon_double_left_click(self, widget, item):
        try:
            wid, tid   = self.window_controller.get_active_data()
            notebook   = self.builder.get_object(f"window_{wid}")
            path_entry = self.builder.get_object(f"path_entry")
            tab_label  = self.get_tab_label_widget_from_widget(notebook, widget)

            view       = self.get_fm_window(wid).get_view_by_id(tid)
            model      = widget.get_model()

            fileName   = model[item][1]
            dir        = view.get_current_directory()
            file       = dir + "/" + fileName
            refresh    = True

            if isdir(file):
                view.set_path(file)
            elif isfile(file):
                refresh = False
                view.open_file_locally(file)

            if refresh == True:
                self.load_store(view, model)
                tab_label.set_label(view.get_end_of_path())
                path_entry.set_text(view.get_current_directory())
        except Exception as e:
            print(repr(e))

    def grid_on_drag_set(self, widget, drag_context, data, info, time):
        action    = widget.get_name()
        store     = widget.get_model()
        treePaths = widget.get_selected_items()
        wid, tid  = action.split("|")
        view      = self.get_fm_window(wid).get_view_by_id(tid)
        dir       = view.get_current_directory()
        uris      = []

        for path in treePaths:
            itr   = store.get_iter(path)
            file  = store.get(itr, 1)[0]
            fpath = f"file://{dir}/{file}"
            uris.append(fpath)

        data.set_uris(uris)
        event_system.push_gui_event(["refresh_tab", None, action])

    def grid_on_drag_motion(self, widget, drag_context, x, y, data):
        wid, tid = widget.get_name().split("|")
        self.window_controller.set_active_data(wid, tid)

    def grid_on_drag_data_received(self, widget, drag_context, x, y, data, info, time):
        if info == 80:
            wid, tid  = self.window_controller.get_active_data()
            notebook  = self.builder.get_object(f"window_{wid}")
            icon_view, tab_label = self.get_icon_view_and_label_from_notebook(notebook, f"{wid}|{tid}")

            view  = self.get_fm_window(wid).get_view_by_id(tid)
            store = icon_view.get_model()
            uris  = data.get_uris()
            dest  = view.get_current_directory()

            if len(uris) > 0:
                print(f"Target Move Path:  {dest}")
                for uri in uris:
                    print(f"URI:  {uri}")
                    self.move_file(view, uri, dest)

                # Reloads new directory
                view.load_directory()
                self.load_store(view, store)

    def create_new_view_notebook(self, widget=None, wid=None, path=None):
        self.create_tab(wid, path)
