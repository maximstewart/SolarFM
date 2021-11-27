# Python imports
import os

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
        fname_field = self.builder.get_object("context_menu_fname")
        file_name   = fname_field.get_text().strip()
        type        = self.builder.get_object("context_menu_type_toggle").get_state()

        wid, tid    = self.window_controller.get_active_data()
        view        = self.get_fm_window(wid).get_view_by_id(tid)
        target      = f"{view.get_current_directory()}"

        if file_name != "":
            file_name = "file://" + target + "/" + file_name
            if type == True:     # Create File
                self.handle_file([file_name], "create_file", target)
            else:                # Create Folder
                self.handle_file([file_name], "create_dir")

        fname_field.set_text("")

    def open_files(self):
        wid, tid  = self.window_controller.get_active_data()
        view      = self.get_fm_window(wid).get_view_by_id(tid)
        iconview  = self.builder.get_object(f"{wid}|{tid}|iconview")
        store     = iconview.get_model()
        uris      = self.format_to_uris(store, wid, tid, self.selected_files, True)

        for file in uris:
            view.open_file_locally(file)

    def open_with_files(self, appchooser_widget):
        wid, tid  = self.window_controller.get_active_data()
        view      = self.get_fm_window(wid).get_view_by_id(tid)
        iconview  = self.builder.get_object(f"{wid}|{tid}|iconview")
        store     = iconview.get_model()
        uris      = self.format_to_uris(store, wid, tid, self.selected_files)

        f         = Gio.File.new_for_uri(uris[0])
        app_info  = appchooser_widget.get_app_info()
        app_info.launch([f], None)

    def edit_files(self):
        pass

    def rename_files(self):
        rename_label = self.builder.get_object("file_to_rename_label")
        rename_input = self.builder.get_object("new_rename_fname")
        wid, tid     = self.window_controller.get_active_data()
        view         = self.get_fm_window(wid).get_view_by_id(tid)
        iconview     = self.builder.get_object(f"{wid}|{tid}|iconview")
        store        = iconview.get_model()
        uris         = self.format_to_uris(store, wid, tid, self.to_rename_files)

        # The rename button hides the rename dialog box which lets the loop continue.
        # Weirdly, the show at the end is needed to flow through all the list properly
        # than auto chosing the first rename entry you do.
        for uri in uris:
            entry = uri.split("/")[-1]
            rename_label.set_label(entry)
            rename_input.set_text(entry)
            if self.skip_edit:
                self.skip_edit = False
                self.show_edit_file_menu()

            # Yes...this step is required even with the above... =/
            self.show_edit_file_menu()

            if self.skip_edit:
                continue
            if self.cancel_edit:
                break

            rname_to = rename_input.get_text().strip()
            target   = f"file://{view.get_current_directory()}/{rname_to}"
            self.handle_file([uri], "edit", target)

            self.show_edit_file_menu()


        self.skip_edit   = False
        self.cancel_edit = False
        self.hide_new_file_menu()
        self.to_rename_files.clear()




    def cut_files(self):
        wid, tid  = self.window_controller.get_active_data()
        iconview  = self.builder.get_object(f"{wid}|{tid}|iconview")
        store     = iconview.get_model()
        uris      = self.format_to_uris(store, wid, tid, self.selected_files)
        self.to_cut_files = uris

    def copy_files(self):
        wid, tid  = self.window_controller.get_active_data()
        iconview  = self.builder.get_object(f"{wid}|{tid}|iconview")
        store     = iconview.get_model()
        uris      = self.format_to_uris(store, wid, tid, self.selected_files)
        self.to_copy_files = uris

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
    def handle_file(self, paths, action, _target_path=None):
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


                if _target_path:
                    if os.path.isdir(_target_path):
                        info    = f.query_info("standard::display-name", 0, cancellable=None)
                        _target = f"file://{_target_path}/{info.get_display_name()}"
                        target  = Gio.File.new_for_uri(_target)
                    else:
                        target  = Gio.File.new_for_uri(_target_path)

                # See if dragging to same directory then break
                if action not in ["trash", "delete", "edit"] and \
                    (f.get_parent().get_path() == target.get_parent().get_path()):
                    break

                type = f.query_file_type(flags=Gio.FileQueryInfoFlags.NONE, cancellable=None)
                if not type == Gio.FileType.DIRECTORY:
                    if action == "delete":
                        f.delete(cancellable=None)
                    if action == "trash":
                        f.trash(cancellable=None)
                    if action == "copy":
                        f.copy(target, flags=Gio.FileCopyFlags.BACKUP, cancellable=None)
                    if action == "move" or action == "edit":
                        f.move(target, flags=Gio.FileCopyFlags.BACKUP, cancellable=None)
                else:
                    wid, tid  = self.window_controller.get_active_data()
                    view      = self.get_fm_window(wid).get_view_by_id(tid)
                    fPath     = f.get_path()
                    tPath     = None

                    if target:
                        tPath = target.get_path()

                    if action == "delete":
                        view.delete_file(fPath)
                    if action == "trash":
                        f.trash(cancellable=None)
                    if action == "copy":
                        view.copy_file(fPath, tPath)
                        # f.copy(target, flags=Gio.FileCopyFlags.BACKUP, cancellable=None)
                    if action == "move" or action == "edit":
                        view.move_file(fPath, tPath)
                        # f.move(target, flags=Gio.FileCopyFlags.BACKUP, cancellable=None)

            except GObject.GError as e:
                raise OSError(e.message)

    def preprocess_paths(self, paths):
        if not isinstance(paths, list):
            paths = [paths]
        # Convert items such as pathlib paths to strings
        paths = [path.__fspath__() if hasattr(path, "__fspath__") else path for path in paths]
        return paths
