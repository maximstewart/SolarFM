# Python imports
import copy
from os.path import isdir, isfile

# Lib imports
import gi

from gi.repository import Gdk

# Application imports
from . import WidgetMixin


class TabMixin(WidgetMixin):
    """docstring for TabMixin"""

    def get_fm_window(self, wid):
        return self.window_controller.get_window_by_nickname(f"window_{wid}")

    def create_tab(self, wid, path=None, save_state=True):
        notebook    = self.builder.get_object(f"window_{wid}")
        path_entry  = self.builder.get_object(f"path_entry")
        view        = self.window_controller.add_view_for_window_by_nickname(f"window_{wid}")
        view.logger = self.logger

        if path: view.set_path(path)

        tab           = self.create_tab_widget(view)
        scroll, store = self.create_grid_iconview_widget(view, wid)
        # scroll, store = self.create_grid_treeview_widget(view, wid)
        index         = notebook.append_page(scroll, tab)

        self.window_controller.set_active_data(wid, view.get_tab_id())
        path_entry.set_text(view.get_current_directory())
        notebook.show_all()
        notebook.set_current_page(index)

        notebook.set_tab_reorderable(scroll, True)
        self.load_store(view, store, save_state)

    def close_tab(self, widget, eve):
        notebook      = widget.get_parent().get_parent()
        page          = notebook.get_current_page()

        tid           = self.get_tab_id_from_widget(widget.get_parent())
        wid           = int(notebook.get_name()[-1])

        self.get_fm_window(wid).delete_view_by_id(tid)
        notebook.remove_page(page)
        self.window_controller.save_state()

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

            if fileName == ".":
                view.load_directory()
            elif fileName == "..":
                view.pop_from_path()
            elif isdir(file):
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


    def grid_icon_single_click(self, widget, eve):
        try:
            wid, tid = widget.get_name().split("|")
            self.window_controller.set_active_data(wid, tid)

            if eve.type == Gdk.EventType.BUTTON_RELEASE and eve.button == 1:   # l-click
                self.set_path_text(wid, tid)

                if self.single_click_open: # FIXME: need to find a way to pass the model index
                    self.icon_double_left_click(widget)
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

            print(f"Target Move Path:  {dest}")
            if len(uris) > 0:
                for uri in uris:
                    print(f"URI:  {uri}")
                    self.move_file(view, uri, dest)

                view.load_directory()
                self.load_store(view, store, False)

    def do_action_from_bar_controls(self, widget, eve=None):
        action    = widget.get_name()
        wid, tid  = self.window_controller.get_active_data()
        notebook  = self.builder.get_object(f"window_{wid}")
        icon_view, tab_label = self.get_icon_view_and_label_from_notebook(notebook, f"{wid}|{tid}")

        view  = self.get_fm_window(wid).get_view_by_id(tid)
        store = icon_view.get_model()

        if action == "go_up":
            view.pop_from_path()
        if action == "go_home":
            view.set_to_home()
        if action == "refresh_view":
            view.load_directory()
        if action == "create_tab" :
            dir = view.get_current_directory()
            self.create_tab(wid, dir)
            return
        if action == "path_entry":
            path      = widget.get_text()
            traversed = view.set_path(path)
            if not traversed:
                return

        self.load_store(view, store, True)
        self.set_path_text(wid, tid)
        tab_label.set_label(view.get_end_of_path())




    # File control events
    def create_file(self):
        pass

    def update_file(self):
        nFile = widget.get_text().strip()
        if data and data.keyval == 65293:    # Enter key event
            view.update_file(nFile)
        elif data == None:                   # Save button 'event'
            view.update_file(nFile)

    def delete_file(self):
        pass


    def move_file(self, view, fFile, tFile):
        view.move_file(fFile.replace("file://", ""), tFile)

    def copy_file(self):
        pass

    def cut_file(self):
        pass

    def paste_file(self):
        pass
