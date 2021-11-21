# Python imports

# Lib imports

# Application imports
from . import WidgetMixin


class TabMixin(WidgetMixin):
    """docstring for TabMixin"""

    def create_tab(self, wid, path=None):
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
        self.load_store(view, store)
        self.set_window_title()

    def close_tab(self, button, eve=None):
        notebook = button.get_parent().get_parent()
        tid      = self.get_tab_id_from_tab_box(button.get_parent())
        wid      = int(notebook.get_name()[-1])
        scroll   = self.builder.get_object(f"{wid}|{tid}")
        page     = notebook.page_num(scroll)

        self.get_fm_window(wid).delete_view_by_id(tid)
        notebook.remove_page(page)
        self.window_controller.save_state()
        self.set_window_title()

    def on_tab_switch_update(self, notebook, content=None, index=None):
        wid, tid = content.get_children()[0].get_name().split("|")
        self.window_controller.set_active_data(wid, tid)
        self.set_path_text(wid, tid)
        self.set_window_title()

    def get_tab_id_from_tab_box(self, tab_box):
        tid = tab_box.get_children()[2]
        return tid.get_text()

    def get_tab_label(self, notebook, iconview):
        return notebook.get_tab_label(iconview.get_parent()).get_children()[0]

    def get_tab_close(self, notebook, iconview):
        return notebook.get_tab_label(iconview.get_parent()).get_children()[1]

    def get_tab_iconview_from_notebook(self, notebook):
        return notebook.get_children()[1].get_children()[0]


    def do_action_from_bar_controls(self, widget, eve=None):
        action    = widget.get_name()
        wid, tid  = self.window_controller.get_active_data()
        notebook  = self.builder.get_object(f"window_{wid}")
        store, tab_label = self.get_store_and_label_from_notebook(notebook, f"{wid}|{tid}")
        view      = self.get_fm_window(wid).get_view_by_id(tid)

        if action == "go_up":
            view.pop_from_path()
        if action == "go_home":
            view.set_to_home()
        if action == "refresh_view":
            view.load_directory()
        if action == "create_tab":
            dir = view.get_current_directory()
            self.create_tab(wid, dir)
            return
        if action == "path_entry":
            path = widget.get_text()
            dir  = view.get_current_directory() + "/"
            if path == dir :
                return

            traversed = view.set_path(path)
            if not traversed:
                return

        self.load_store(view, store)
        self.set_path_text(wid, tid)
        tab_label.set_label(view.get_end_of_path())
        self.set_window_title()

    def keyboard_close_tab(self):
        wid, tid  = self.window_controller.get_active_data()
        notebook  = self.builder.get_object(f"window_{wid}")
        iconview  = self.get_tab_iconview_from_notebook(notebook)
        close     = self.get_tab_close(notebook, iconview)
        close.released()

    # File control events
    def show_hide_hidden_files(self):
        wid, tid = self.window_controller.get_active_data()
        view     = self.get_fm_window(wid).get_view_by_id(tid)
        view.hide_hidden = not view.hide_hidden
        view.load_directory()
        self.builder.get_object("refresh_view").released()


    def get_uris(self, store, treePaths=None):
        uris = []

        for path in treePaths:
            itr   = store.get_iter(path)
            file  = store.get(itr, 1)[0]
            fpath = f"file://{dir}/{file}"
            uris.append(fpath)

        return uris

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

    def menu_bar_copy(self, widget, eve):
        self.copy_file()

    def copy_file(self):
        wid, tid  = self.window_controller.get_active_data()
        print(wid)
        print(tid)
        notebook  = self.builder.get_object(f"window_{wid}")
        iconview  = self.get_tab_iconview_from_notebook(notebook)
        print(iconview)
        store     = iconview.get_model()
        treePaths = iconview.get_selected_items()

        print(len(treePaths))
        for path in treePaths:
            itr   = store.get_iter(path)
            file  = store.get(itr, 1)[0]
            print(file)

        # uris      = self.get_uris(store, treePaths)
        # print(uris)


    def cut_file(self):
        pass

    def paste_file(self):
        pass
