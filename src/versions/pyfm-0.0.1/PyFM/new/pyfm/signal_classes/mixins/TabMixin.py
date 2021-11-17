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

    def close_tab(self, widget, eve):
        notebook = widget.get_parent().get_parent()
        page     = notebook.get_current_page()
        tid      = self.get_tab_id_from_widget(widget.get_parent())
        wid      = int(notebook.get_name()[-1])

        self.get_fm_window(wid).delete_view_by_id(tid)
        notebook.remove_page(page)
        self.window_controller.save_state()
        self.set_window_title()

    def on_tab_switch_update(self, notebook, content=None, index=None):
        wid, tid   = content.get_children()[0].get_name().split("|")
        self.window_controller.set_active_data(wid, tid)
        self.set_path_text(wid, tid)
        self.set_window_title()

    def get_tab_id_from_widget(self, tab_box):
        tid = tab_box.get_children()[2]
        return tid.get_text()

    def get_tab_label_widget_from_widget(self, notebook, widget):
        return notebook.get_tab_label(widget.get_parent()).get_children()[0]


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
        if action == "create_tab":
            dir = view.get_current_directory()
            self.create_tab(wid, dir)
            return
        if action == "path_entry":
            path      = widget.get_text()
            traversed = view.set_path(path)
            if not traversed:
                return

        self.load_store(view, store)
        self.set_path_text(wid, tid)
        tab_label.set_label(view.get_end_of_path())
        self.set_window_title()


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
