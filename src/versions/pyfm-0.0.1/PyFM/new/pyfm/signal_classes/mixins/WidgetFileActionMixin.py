# Python imports

# Lib imports
from gi.repository import GObject, Gio

# Application imports



class WidgetFileActionMixin:
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

    def create_file(self):
        file_name = self.builder.get_object("context_menu_fname").get_text().strip()
        type      = self.builder.get_object("context_menu_type_toggle").get_state()

        wid, tid  = self.window_controller.get_active_data()
        view      = self.get_fm_window(wid).get_view_by_id(tid)
        target    = f"{view.get_current_directory()}"

        if file_name != "":
            file_name = "file://" + target + "/" + file_name
            if type == True:     # Create File
                self.handle_file([file_name], "create_file", target)
            else:                # Create Folder
                self.handle_file([file_name], "create_dir")

    def update_file(self):
        pass

    def menu_bar_copy(self, widget, eve):
        self.copy_file()

    def open_files(self):
        wid, tid  = self.window_controller.get_active_data()
        view      = self.get_fm_window(wid).get_view_by_id(tid)
        iconview  = self.builder.get_object(f"{wid}|{tid}|iconview")
        store     = iconview.get_model()
        uris      = self.format_to_uris(store, wid, tid, self.selected_files, True)

        for file in uris:
            view.open_file_locally(file)

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
        target    = f"{view.get_current_directory()}"

        if len(self.to_copy_files) > 0:
            self.handle_file(self.to_copy_files, "copy", target)
        elif len(self.to_cut_files) > 0:
            self.handle_file(self.to_cut_files, "move", target)


    def move_file(self, view, files, target):
        self.handle_file([files], "move", target)

    def delete_files(self):
        wid, tid  = self.window_controller.get_active_data()
        iconview  = self.builder.get_object(f"{wid}|{tid}|iconview")
        view      = self.get_fm_window(wid).get_view_by_id(tid)
        store     = iconview.get_model()
        uris      = self.format_to_uris(store, wid, tid, self.selected_files)
        self.handle_file(uris, "delete")

    def trash_files(self):
        wid, tid  = self.window_controller.get_active_data()
        iconview  = self.builder.get_object(f"{wid}|{tid}|iconview")
        view      = self.get_fm_window(wid).get_view_by_id(tid)
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

                if action == "create_file":
                    f.create(Gio.FileCreateFlags.NONE, cancellable=None)
                    break
                if action == "create_dir":
                    f.make_directory(cancellable=None)
                    break


                if base_dir:
                    info    = f.query_info("standard::display-name", 0, cancellable=None)
                    _target = f"file://{base_dir}/{info.get_display_name()}"
                    target  = Gio.File.new_for_uri(_target)

                # See if dragging to same directory then break
                if action != "trash" and action != "delete" and \
                    (f.get_parent().get_path() == target.get_parent().get_path()):
                    break

                if action == "delete":
                    f.delete(cancellable=None)
                if action == "trash":
                    f.trash(cancellable=None)
                if action == "copy":
                    f.copy(target, flags=Gio.FileCopyFlags.BACKUP, cancellable=None)
                if action == "move":
                    f.move(target, flags=Gio.FileCopyFlags.BACKUP, cancellable=None)
            except GObject.GError as e:
                raise OSError(e.message)

    def preprocess_paths(self, paths):
        if not isinstance(paths, list):
            paths = [paths]
        # Convert items such as pathlib paths to strings
        paths = [path.__fspath__() if hasattr(path, "__fspath__") else path for path in paths]
        return paths
