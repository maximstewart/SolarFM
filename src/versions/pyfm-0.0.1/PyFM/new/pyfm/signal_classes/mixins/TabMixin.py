# Python imports

# Lib imports
from gi.repository import GObject, Gio


# Application imports
from . import WidgetMixin


class TabMixin(WidgetMixin):
    """docstring for TabMixin"""

    def create_tab(self, wid, path=None):
        notebook    = self.builder.get_object(f"window_{wid}")
        path_entry  = self.builder.get_object(f"path_entry")
        view        = self.window_controller.add_view_for_window_by_nickname(f"window_{wid}")
        view.logger = self.logger

        view.set_wid(wid)
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
        self.set_file_watcher(view)

    def set_file_watcher(self, view):
        if view.get_dir_watcher():
            watcher = view.get_dir_watcher()
            watcher.cancel()
            if debug:
                print(f"Watcher Is Cancelled:  {watcher.is_cancelled()}")

        dir_watcher  = Gio.File.new_for_path(view.get_current_directory()) \
                                .monitor_directory(Gio.FileMonitorFlags.WATCH_MOVES,
                                                    Gio.Cancellable()
                                                    )

        wid = view.get_wid()
        tid = view.get_tab_id()
        dir_watcher.connect("changed", self.dir_watch_updates, (f"{wid}|{tid}",))
        view.set_dir_watcher(dir_watcher)

    def dir_watch_updates(self, file_monitor, file, other_file=None, eve_type=None, data=None):
        if eve_type ==  Gio.FileMonitorEvent.CREATED or \
            eve_type ==  Gio.FileMonitorEvent.DELETED or \
            eve_type == Gio.FileMonitorEvent.RENAMED or \
            eve_type == Gio.FileMonitorEvent.MOVED_IN or \
            eve_type == Gio.FileMonitorEvent.MOVED_OUT:
                wid, tid  = data[0].split("|")
                notebook  = self.builder.get_object(f"window_{wid}")
                view      = self.get_fm_window(wid).get_view_by_id(tid)
                iconview  = self.builder.get_object(f"{wid}|{tid}|iconview")
                store     = iconview.get_model()
                _store, tab_label = self.get_store_and_label_from_notebook(notebook, f"{wid}|{tid}")

                view.load_directory()
                self.load_store(view, store)
                tab_label.set_label(view.get_end_of_path())


    def close_tab(self, button, eve=None):
        notebook = button.get_parent().get_parent()
        tid      = self.get_tab_id_from_tab_box(button.get_parent())
        wid      = int(notebook.get_name()[-1])
        scroll   = self.builder.get_object(f"{wid}|{tid}")
        page     = notebook.page_num(scroll)
        view     = self.get_fm_window(wid).get_view_by_id(tid)
        watcher  = view.get_dir_watcher()
        watcher.cancel()

        self.get_fm_window(wid).delete_view_by_id(tid)
        notebook.remove_page(page)
        self.window_controller.save_state()
        self.set_window_title()

    def on_tab_switch_update(self, notebook, content=None, index=None):
        self.selected_files.clear()
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
        self.set_file_watcher(view)


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


    def create_file(self):
        pass

    def update_file(self):
        nFile = widget.get_text().strip()
        if data and data.keyval == 65293:    # Enter key event
            view.update_file(nFile)
        elif data == None:                   # Save button 'event'
            view.update_file(nFile)

    def menu_bar_copy(self, widget, eve):
        self.copy_file()

    def copy_files(self):
        wid, tid  = self.window_controller.get_active_data()
        iconview  = self.builder.get_object(f"{wid}|{tid}|iconview")
        store     = iconview.get_model()
        uris      = self.format_to_uris(store, wid, tid, self.selected_files)
        self.to_copy_files = uris

    def cut_files(self):
        wid, tid  = self.window_controller.get_active_data()
        iconview  = self.builder.get_object(f"{wid}|{tid}|iconview")
        store     = iconview.get_model()
        uris      = self.format_to_uris(store, wid, tid, self.selected_files)
        self.to_cut_files = uris

    def paste_files(self):
        wid, tid  = self.window_controller.get_active_data()
        view      = self.get_fm_window(wid).get_view_by_id(tid)
        to_path   = f"{view.get_current_directory()}"

        if len(self.to_copy_files) > 0:
            self.handle_file(self.to_copy_files, "copy", to_path)
        else:
            self.handle_file(self.to_cut_files, "move", to_path)


    def move_file(self, view, fFile, tFile):
        self.handle_file([fFile], "move", tFile)

    def delete_files(self):
        pass

    def trash_files(self):
        wid, tid  = self.window_controller.get_active_data()
        view      = self.get_fm_window(wid).get_view_by_id(tid)
        iconview  = self.builder.get_object(f"{wid}|{tid}|iconview")
        store     = iconview.get_model()
        uris      = self.format_to_uris(store, wid, tid, self.selected_files)
        self.handle_file(uris, "trash")


    # NOTE: Gio moves files by generating the target file path with name in it
    #       We can't just give a base target directory and run with it.
    #       Also, the display name is UTF-8 safe and meant for displaying in GUIs
    def handle_file(self, paths, action, base_dir=None):
        paths  = self.preprocess_paths(paths)
        target = None

        for path in paths:
            try:
                f = Gio.File.new_for_uri(path)
                if base_dir:
                    info    = f.query_info("standard::display-name", 0, cancellable=None)
                    _target = f"file://{base_dir}/{info.get_display_name()}"
                    target  = Gio.File.new_for_uri(_target)

                if action == "trash":
                    f.trash(cancellable=None)
                if action == "copy":
                    f.copy(target, flags=Gio.FileCopyFlags.OVERWRITE, cancellable=None)
                if action == "move":
                    f.move(target, flags=Gio.FileCopyFlags.OVERWRITE, cancellable=None)
            except GObject.GError as e:
                raise OSError(e.message)

    def preprocess_paths(self, paths):
        if not isinstance(paths, list):
            paths = [paths]
        # Convert items such as pathlib paths to strings
        paths = [path.__fspath__() if hasattr(path, "__fspath__") else path for path in paths]
        return paths
