# Python imports
import os

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, Gio

# Application imports



class WidgetFileActionMixin:
    def set_file_watcher(self, view):
        if view.get_dir_watcher():
            watcher = view.get_dir_watcher()
            watcher.cancel()
            if debug:
                print(f"Watcher Is Cancelled:  {watcher.is_cancelled()}")

        cur_dir = view.get_current_directory()
        # Temp updating too much with current events we are checking for.
        # Causes invalid iter errors in WidbetMixin > update_store
        if cur_dir == "/tmp":
            watcher = None
            return

        dir_watcher  = Gio.File.new_for_path(cur_dir) \
                                .monitor_directory(Gio.FileMonitorFlags.WATCH_MOVES, Gio.Cancellable())

        wid = view.get_wid()
        tid = view.get_tab_id()
        dir_watcher.connect("changed", self.dir_watch_updates, (f"{wid}|{tid}",))
        view.set_dir_watcher(dir_watcher)

    def dir_watch_updates(self, file_monitor, file, other_file=None, eve_type=None, data=None):
        if eve_type in  [Gio.FileMonitorEvent.CREATED, Gio.FileMonitorEvent.DELETED,
                        Gio.FileMonitorEvent.RENAMED, Gio.FileMonitorEvent.MOVED_IN,
                                                    Gio.FileMonitorEvent.MOVED_OUT]:
                if debug:
                    print(eve_type)

                wid, tid  = data[0].split("|")
                notebook  = self.builder.get_object(f"window_{wid}")
                view      = self.get_fm_window(wid).get_view_by_id(tid)
                iconview  = self.builder.get_object(f"{wid}|{tid}|iconview")
                store     = iconview.get_model()
                _store, tab_label = self.get_store_and_label_from_notebook(notebook, f"{wid}|{tid}")

                view.load_directory()
                self.load_store(view, store)
                tab_label.set_label(view.get_end_of_path())
                self.set_bottom_labels(view)




    def create_file(self):
        fname_field = self.builder.get_object("context_menu_fname")
        file_name   = fname_field.get_text().strip()
        type        = self.builder.get_object("context_menu_type_toggle").get_state()

        wid, tid    = self.window_controller.get_active_data()
        view        = self.get_fm_window(wid).get_view_by_id(tid)
        target      = f"{view.get_current_directory()}"

        if file_name:
            file_name = "file://" + target + "/" + file_name
            if type == True:     # Create File
                self.handle_file([file_name], "create_file")
            else:                # Create Folder
                self.handle_file([file_name], "create_dir")

        fname_field.set_text("")


    def get_current_state(self):
        wid, tid     = self.window_controller.get_active_data()
        view         = self.get_fm_window(wid).get_view_by_id(tid)
        iconview     = self.builder.get_object(f"{wid}|{tid}|iconview")
        store        = iconview.get_model()
        return wid, tid, view, iconview, store

    def execute_files(self, in_terminal=False):
        wid, tid, view, iconview, store = self.get_current_state()
        paths       = self.format_to_uris(store, wid, tid, self.selected_files, True)
        current_dir = view.get_current_directory()
        command     = None

        for path in paths:
            command = f"sh -c '{path}'" if not in_terminal else f"{view.terminal_app} -e '{path}'"
            self.execute(command, current_dir)


    def open_files(self):
        wid, tid, view, iconview, store = self.get_current_state()
        uris = self.format_to_uris(store, wid, tid, self.selected_files, True)

        for file in uris:
            view.open_file_locally(file)

    def open_with_files(self, appchooser_widget):
        wid, tid, view, iconview, store = self.get_current_state()
        uris      = self.format_to_uris(store, wid, tid, self.selected_files)
        file      = Gio.File.new_for_uri(uris[0])
        app_info  = appchooser_widget.get_app_info()

        app_info.launch([file], None)

    def rename_files(self):
        rename_label = self.builder.get_object("file_to_rename_label")
        rename_input = self.builder.get_object("new_rename_fname")
        wid, tid, view, iconview, store = self.get_current_state()
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

    def archive_files(self, archiver_dialogue):
        wid, tid, view, iconview, store = self.get_current_state()
        paths = self.format_to_uris(store, wid, tid, self.selected_files)

        save_target        = archiver_dialogue.get_filename();
        start_itr, end_itr = self.arc_command_buffer.get_bounds()
        command            = self.arc_command_buffer.get_text(start_itr, end_itr, False)

        command            = command.replace("%o", save_target)
        command            = command.replace("%N", ' '.join(paths))
        final_command      = f"terminator -e '{command}'"
        self.execute(final_command, start_dir=None, use_os_system=True)



    def cut_files(self):
        wid, tid, view, iconview, store = self.get_current_state()
        uris      = self.format_to_uris(store, wid, tid, self.selected_files)
        self.to_cut_files = uris

    def copy_files(self):
        wid, tid, view, iconview, store = self.get_current_state()
        print(self.selected_files)
        uris      = self.format_to_uris(store, wid, tid, self.selected_files)
        print(uris)
        self.to_copy_files = uris

    def paste_files(self):
        wid, tid  = self.window_controller.get_active_data()
        view      = self.get_fm_window(wid).get_view_by_id(tid)
        target    = f"file://{view.get_current_directory()}"

        if len(self.to_copy_files) > 0:
            self.handle_file(self.to_copy_files, "copy", target)
        elif len(self.to_cut_files) > 0:
            self.handle_file(self.to_cut_files, "move", target)




    def move_files(self, files, target):
        self.handle_file(files, "move", target)

    def delete_files(self):
        wid, tid, view, iconview, store = self.get_current_state()
        uris      = self.format_to_uris(store, wid, tid, self.selected_files)
        self.handle_file(uris, "delete")

    def trash_files(self):
        wid, tid, view, iconview, store = self.get_current_state()
        uris      = self.format_to_uris(store, wid, tid, self.selected_files)
        self.handle_file(uris, "trash")




    # NOTE: While not fully race condition proof, we happy path it first
    #       and then handle anything after as a conflict for renaming before
    #       copy, move, or edit. This is literally the oppopsite of what Gtk says to do.
    #       But, they can't even delete directories properly. So... f**k them.
    def handle_file(self, paths, action, _target_path=None):
        paths    = self.preprocess_paths(paths)
        target   = None
        response = None
        self.warning_alert.format_secondary_text(f"Do you really want to {action} the {len(paths)} file(s)?")

        for path in paths:
            try:
                file = Gio.File.new_for_uri(path)

                if action == "trash":
                    file.trash(cancellable=None)

                if (action == "create_file" or action == "create_dir") and not file.query_exists():
                    if action == "create_file":
                        file.create(flags=Gio.FileCreateFlags.NONE, cancellable=None)
                        continue
                    if action == "create_dir":
                        file.make_directory(cancellable=None)
                        continue


                if _target_path:
                    if os.path.isdir(_target_path.split("file://")[1]):
                        info    = file.query_info("standard::display-name", 0, cancellable=None)
                        _target = f"{_target_path}/{info.get_display_name()}"
                        target  = Gio.File.new_for_uri(_target)
                    else:
                        target  = Gio.File.new_for_uri(_target_path)

                if target and not target.query_exists():
                    type = file.query_file_type(flags=Gio.FileQueryInfoFlags.NONE)

                    if type == Gio.FileType.DIRECTORY:
                        wid, tid  = self.window_controller.get_active_data()
                        view      = self.get_fm_window(wid).get_view_by_id(tid)
                        fPath     = file.get_path()
                        tPath     = None
                        state     = True

                        if action == "copy":
                            tPath = target.get_path()
                            view.copy_file(fPath, tPath)
                        if action == "move" or action == "edit":
                            tPath = target.get_parent().get_path()
                            view.move_file(fPath, tPath)
                    else:
                        if action == "copy":
                            file.copy(target, flags=Gio.FileCopyFlags.BACKUP, cancellable=None)
                        if action == "move" or action == "edit":
                            file.move(target, flags=Gio.FileCopyFlags.BACKUP, cancellable=None)




                # NOTE: Past here, we need to handle detected conflicts.
                #       Maybe create a collection of file and target pares
                #       that then get passed to a handler who calls show_exists_page?

                if action == "delete":
                    if not response:
                        response = self.warning_alert.run()
                        self.warning_alert.hide()
                    if response == Gtk.ResponseType.YES:
                        type = file.query_file_type(flags=Gio.FileQueryInfoFlags.NONE)

                        if type == Gio.FileType.DIRECTORY:
                            wid, tid  = self.window_controller.get_active_data()
                            view      = self.get_fm_window(wid).get_view_by_id(tid)
                            view.delete_file( file.get_path() )
                        else:
                            file.delete(cancellable=None)
                    else:
                        break


            except GObject.GError as e:
                raise OSError(e)


    def preprocess_paths(self, paths):
        if not isinstance(paths, list):
            paths = [paths]
        # Convert items such as pathlib paths to strings
        paths = [path.__fspath__() if hasattr(path, "__fspath__") else path for path in paths]
        return paths
