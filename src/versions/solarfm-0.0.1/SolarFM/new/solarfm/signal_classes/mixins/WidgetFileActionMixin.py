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




    def open_files(self):
        wid, tid, view, iconview, store = self.get_current_state()
        uris = self.format_to_uris(store, wid, tid, self.selected_files, True)

        for file in uris:
            view.open_file_locally(file)

    def open_with_files(self, appchooser_widget):
        wid, tid, view, iconview, store = self.get_current_state()
        app_info  = appchooser_widget.get_app_info()
        uris      = self.format_to_uris(store, wid, tid, self.selected_files)

        app_info.launch_uris_async(uris)

    def execute_files(self, in_terminal=False):
        wid, tid, view, iconview, store = self.get_current_state()
        paths       = self.format_to_uris(store, wid, tid, self.selected_files, True)
        current_dir = view.get_current_directory()
        command     = None

        for path in paths:
            command = f"exec '{path}'" if not in_terminal else f"{view.terminal_app} -e '{path}'"
            view.execute(command, start_dir=view.get_current_directory(), use_os_system=False)

    def archive_files(self, archiver_dialogue):
        wid, tid, view, iconview, store = self.get_current_state()
        paths = self.format_to_uris(store, wid, tid, self.selected_files, True)

        save_target = archiver_dialogue.get_filename();
        sItr, eItr  = self.arc_command_buffer.get_bounds()
        pre_command = self.arc_command_buffer.get_text(sItr, eItr, False)
        pre_command = pre_command.replace("%o", save_target)
        pre_command = pre_command.replace("%N", ' '.join(paths))
        command     = f"{view.terminal_app} -e '{pre_command}'"

        view.execute(command, start_dir=None, use_os_system=True)

    def rename_files(self):
        rename_label = self.builder.get_object("file_to_rename_label")
        rename_input = self.builder.get_object("new_rename_fname")
        wid, tid, view, iconview, store = self.get_current_state()
        uris         = self.format_to_uris(store, wid, tid, self.selected_files)

        for uri in uris:
            entry = uri.split("/")[-1]
            rename_label.set_label(entry)
            rename_input.set_text(entry)

            self.show_edit_file_menu()
            if self.skip_edit:
                self.skip_edit   = False
                continue
            if self.cancel_edit:
                self.cancel_edit = False
                break

            rname_to = rename_input.get_text().strip()
            target   = f"file://{view.get_current_directory()}/{rname_to}"
            self.handle_files([uri], "rename", target)


        self.skip_edit   = False
        self.cancel_edit = False
        self.hide_edit_file_menu()
        self.selected_files.clear()

    def cut_files(self):
        wid, tid, view, iconview, store = self.get_current_state()
        uris = self.format_to_uris(store, wid, tid, self.selected_files)
        self.to_cut_files = uris

    def copy_files(self):
        wid, tid, view, iconview, store = self.get_current_state()
        uris = self.format_to_uris(store, wid, tid, self.selected_files)
        self.to_copy_files = uris

    def paste_files(self):
        wid, tid  = self.window_controller.get_active_data()
        view      = self.get_fm_window(wid).get_view_by_id(tid)
        target    = f"file://{view.get_current_directory()}"

        if len(self.to_copy_files) > 0:
            self.handle_files(self.to_copy_files, "copy", target)
        elif len(self.to_cut_files) > 0:
            self.handle_files(self.to_cut_files, "move", target)

    def delete_files(self):
        wid, tid, view, iconview, store = self.get_current_state()
        uris     = self.format_to_uris(store, wid, tid, self.selected_files)
        response = None

        self.warning_alert.format_secondary_text(f"Do you really want to delete the {len(uris)} file(s)?")
        for uri in uris:
            file = Gio.File.new_for_uri(uri)

            if not response:
                response = self.warning_alert.run()
                self.warning_alert.hide()
            if response == Gtk.ResponseType.YES:
                type = file.query_file_type(flags=Gio.FileQueryInfoFlags.NONE)

                if type == Gio.FileType.DIRECTORY:
                    view.delete_file( file.get_path() )
                else:
                    file.delete(cancellable=None)
            else:
                break


    def trash_files(self):
        wid, tid, view, iconview, store = self.get_current_state()
        uris      = self.format_to_uris(store, wid, tid, self.selected_files)
        for uri in uris:
            file = Gio.File.new_for_uri(uri)
            file.trash(cancellable=None)




    def create_files(self):
        fname_field = self.builder.get_object("context_menu_fname")
        file_name   = fname_field.get_text().strip()
        type        = self.builder.get_object("context_menu_type_toggle").get_state()

        wid, tid    = self.window_controller.get_active_data()
        view        = self.get_fm_window(wid).get_view_by_id(tid)
        target      = f"{view.get_current_directory()}"

        if file_name:
            path = f"file://{target}/{file_name}"

            if type == True:     # Create File
                self.handle_files([path], "create_file")
            else:                # Create Folder
                self.handle_files([path], "create_dir")

        fname_field.set_text("")

    def move_files(self, files, target):
        self.handle_files(files, "move", target)

    # NOTE: Gtk recommends using fail flow than pre check existence which is more
    #       race condition proof. They're right; but, they can't even delete
    #       directories properly. So... f**k them. I'll do it my way.
    def handle_files(self, paths, action, _target_path=None):
        target          = None
        _file           = None
        response        = None
        overwrite_all   = False
        rename_auto_all = False

        for path in paths:
            try:
                file = Gio.File.new_for_uri(path)

                if _target_path:
                    if os.path.isdir(_target_path.split("file://")[1]):
                        info    = file.query_info("standard::display-name", 0, cancellable=None)
                        _target = f"{_target_path}/{info.get_display_name()}"
                        _file   = Gio.File.new_for_uri(_target)
                    else:
                        _file   = Gio.File.new_for_uri(_target_path)
                else:
                    _file = Gio.File.new_for_uri(path)


                if _file.query_exists():
                    if not overwrite_all and not rename_auto_all:
                        self.exists_file_label.set_label(_file.get_basename())
                        self.exists_file_field.set_text(_file.get_basename())
                        response = self.show_exists_page()

                    if response == "overwrite_all":
                        overwrite_all   = True
                    if response == "rename_auto_all":
                        rename_auto_all = True

                    if response == "rename":
                        base_path = _file.get_parent().get_path()
                        new_name  = self.exists_file_field.get_text().strip()
                        rfPath    = f"{base_path}/{new_name}"
                        _file     = Gio.File.new_for_path(rfPath)

                    if response == "rename_auto" or rename_auto_all:
                        _file = self.rename_proc(_file)

                    if response == "overwrite" or overwrite_all:
                        type      = _file.query_file_type(flags=Gio.FileQueryInfoFlags.NONE)

                        if type == Gio.FileType.DIRECTORY:
                            wid, tid  = self.window_controller.get_active_data()
                            view      = self.get_fm_window(wid).get_view_by_id(tid)
                            view.delete_file( _file.get_path() )
                        else:
                            _file.delete(cancellable=None)

                    if response == "skip":
                        continue
                    if response == "skip_all":
                        break

                if _target_path:
                    target = _file
                else:
                    file   = _file


                if action == "create_file":
                    file.create(flags=Gio.FileCreateFlags.NONE, cancellable=None)
                    continue
                if action == "create_dir":
                    file.make_directory(cancellable=None)
                    continue


                type = file.query_file_type(flags=Gio.FileQueryInfoFlags.NONE)
                if type == Gio.FileType.DIRECTORY:
                    wid, tid  = self.window_controller.get_active_data()
                    view      = self.get_fm_window(wid).get_view_by_id(tid)
                    fPath     = file.get_path()
                    tPath     = target.get_path()
                    state     = True

                    if action == "copy":
                        view.copy_file(fPath, tPath)
                    if action == "move" or action == "rename":
                        view.move_file(fPath, tPath)
                else:
                    if action == "copy":
                        file.copy(target, flags=Gio.FileCopyFlags.BACKUP, cancellable=None)
                    if action == "move" or action == "rename":
                        file.move(target, flags=Gio.FileCopyFlags.BACKUP, cancellable=None)

            except GObject.GError as e:
                raise OSError(e)

        self.exists_file_rename_bttn.set_sensitive(False)



    def rename_proc(self, gio_file):
        full_path = gio_file.get_path()
        base_path = gio_file.get_parent().get_path()
        file_name = os.path.splitext(gio_file.get_basename())[0]
        extension = os.path.splitext(full_path)[-1]
        target    = Gio.File.new_for_path(full_path)

        if debug:
            print(f"Path:  {full_path}")
            print(f"Base Path:  {base_path}")
            print(f'Name:  {file_name}')
            print(f"Extension:  {extension}")

        i = 2
        while target.query_exists():
            target = Gio.File.new_for_path(f"{base_path}/{file_name}-copy{i}{extension}")
            i += 1

        return target


    def exists_rename_field_changed(self, widget):
        nfile_name = widget.get_text().strip()
        ofile_name = self.exists_file_label.get_label()

        if nfile_name:
            if nfile_name == ofile_name:
                self.exists_file_rename_bttn.set_sensitive(False)
            else:
                self.exists_file_rename_bttn.set_sensitive(True)
        else:
            self.exists_file_rename_bttn.set_sensitive(False)
