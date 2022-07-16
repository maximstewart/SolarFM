# Python imports
import os, time, threading

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, GLib, Gio

# Application imports


def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs, daemon=True).start()
    return wrapper


class WidgetFileActionMixin:
    """docstring for WidgetFileActionMixin"""

    def sizeof_fmt(self, num, suffix="B"):
        for unit in ["", "K", "M", "G", "T", "Pi", "Ei", "Zi"]:
            if abs(num) < 1024.0:
                return f"{num:3.1f} {unit}{suffix}"
            num /= 1024.0
        return f"{num:.1f} Yi{suffix}"

    def get_dir_size(self, sdir):
        """Get the size of a directory.  Based on code found online."""
        size = os.path.getsize(sdir)

        for item in os.listdir(sdir):
            item = os.path.join(sdir, item)

            if os.path.isfile(item):
                size = size + os.path.getsize(item)
            elif os.path.isdir(item):
                size = size + self.get_dir_size(item)

        return size


    def set_file_watcher(self, tab):
        if tab.get_dir_watcher():
            watcher = tab.get_dir_watcher()
            watcher.cancel()
            if debug:
                print(f"Watcher Is Cancelled:  {watcher.is_cancelled()}")

        cur_dir = tab.get_current_directory()

        dir_watcher  = Gio.File.new_for_path(cur_dir) \
                                .monitor_directory(Gio.FileMonitorFlags.WATCH_MOVES, Gio.Cancellable())

        wid = tab.get_wid()
        tid = tab.get_id()
        dir_watcher.connect("changed", self.dir_watch_updates, (f"{wid}|{tid}",))
        tab.set_dir_watcher(dir_watcher)

    # NOTE: Too lazy to impliment a proper update handler and so just regen store and update tab.
    #       Use a lock system to prevent too many update calls for certain instances but user can manually refresh if they have urgency
    def dir_watch_updates(self, file_monitor, file, other_file=None, eve_type=None, data=None):
        if eve_type in  [Gio.FileMonitorEvent.CREATED, Gio.FileMonitorEvent.DELETED,
                        Gio.FileMonitorEvent.RENAMED, Gio.FileMonitorEvent.MOVED_IN,
                        Gio.FileMonitorEvent.MOVED_OUT]:
                if debug:
                    print(eve_type)

                if eve_type in [Gio.FileMonitorEvent.MOVED_IN, Gio.FileMonitorEvent.MOVED_OUT]:
                    self.update_on_soft_lock_end(data[0])
                elif data[0] in self.soft_update_lock.keys():
                    self.soft_update_lock[data[0]]["last_update_time"] = time.time()
                else:
                    self.soft_lock_countdown(data[0])

    @threaded
    def soft_lock_countdown(self, tab_widget):
        self.soft_update_lock[tab_widget] = { "last_update_time": time.time()}

        lock = True
        while lock:
            time.sleep(0.6)
            last_update_time = self.soft_update_lock[tab_widget]["last_update_time"]
            current_time     = time.time()
            if (current_time - last_update_time) > 0.6:
                lock = False


        self.soft_update_lock.pop(tab_widget, None)
        GLib.idle_add(self.update_on_soft_lock_end, *(tab_widget,))


    def update_on_soft_lock_end(self, tab_widget):
        wid, tid  = tab_widget.split("|")
        notebook  = self.builder.get_object(f"window_{wid}")
        tab       = self.get_fm_window(wid).get_tab_by_id(tid)
        icon_grid = self.builder.get_object(f"{wid}|{tid}|icon_grid")
        store     = icon_grid.get_model()
        _store, tab_widget_label = self.get_store_and_label_from_notebook(notebook, f"{wid}|{tid}")

        tab.load_directory()
        self.load_store(tab, store)

        tab_widget_label.set_label(tab.get_end_of_path())

        _wid, _tid, _tab, _icon_grid, _store = self.get_current_state()

        if [wid, tid] in [_wid, _tid]:
            self.set_bottom_labels(tab)


    def popup_search_files(self, wid, keyname):
        entry = self.builder.get_object(f"win{wid}_search_field")
        self.builder.get_object(f"win{wid}_search").popup()
        entry.set_text(keyname)
        entry.grab_focus_without_selecting()
        entry.set_position(-1)

    def do_file_search(self, widget, eve=None):
        query = widget.get_text()
        self.search_icon_grid.unselect_all()
        for i, file in enumerate(self.search_tab.get_files()):
            if query and query in file[0].lower():
                path = Gtk.TreePath().new_from_indices([i])
                self.search_icon_grid.select_path(path)

        items = self.search_icon_grid.get_selected_items()
        if len(items) == 1:
            self.search_icon_grid.scroll_to_path(items[0], True, 0.5, 0.5)


    def open_files(self):
        wid, tid, tab, icon_grid, store = self.get_current_state()
        uris = self.format_to_uris(store, wid, tid, self.selected_files, True)

        for file in uris:
            tab.open_file_locally(file)

    def open_with_files(self, appchooser_widget):
        wid, tid, tab, icon_grid, store = self.get_current_state()
        app_info  = appchooser_widget.get_app_info()
        uris      = self.format_to_uris(store, wid, tid, self.selected_files)

        tab.app_chooser_exec(app_info, uris)

    def execute_files(self, in_terminal=False):
        wid, tid, tab, icon_grid, store = self.get_current_state()
        paths       = self.format_to_uris(store, wid, tid, self.selected_files, True)
        current_dir = tab.get_current_directory()
        command     = None

        for path in paths:
            command = f"exec '{path}'" if not in_terminal else f"{tab.terminal_app} -e '{path}'"
            tab.execute(command, start_dir=tab.get_current_directory(), use_os_system=False)

    def archive_files(self, archiver_dialogue):
        wid, tid, tab, icon_grid, store = self.get_current_state()
        paths = self.format_to_uris(store, wid, tid, self.selected_files, True)

        save_target = archiver_dialogue.get_filename();
        sItr, eItr  = self.arc_command_buffer.get_bounds()
        pre_command = self.arc_command_buffer.get_text(sItr, eItr, False)
        pre_command = pre_command.replace("%o", save_target)
        pre_command = pre_command.replace("%N", ' '.join(paths))
        command     = f"{tab.terminal_app} -e '{pre_command}'"

        tab.execute(command, start_dir=None, use_os_system=True)

    def rename_files(self):
        rename_label = self.builder.get_object("file_to_rename_label")
        rename_input = self.builder.get_object("new_rename_fname")
        wid, tid, tab, icon_grid, store = self.get_current_state()
        uris         = self.format_to_uris(store, wid, tid, self.selected_files, True)

        for uri in uris:
            entry = uri.split("/")[-1]
            rename_label.set_label(entry)
            rename_input.set_text(entry)

            self.show_edit_file_menu(rename_input)
            if self.skip_edit:
                self.skip_edit   = False
                continue
            if self.cancel_edit:
                self.cancel_edit = False
                break

            rname_to = rename_input.get_text().strip()
            target   = f"{tab.get_current_directory()}/{rname_to}"
            self.handle_files([uri], "rename", target)


        self.skip_edit   = False
        self.cancel_edit = False
        self.hide_edit_file_menu()
        self.selected_files.clear()

    def cut_files(self):
        wid, tid, tab, icon_grid, store = self.get_current_state()
        uris = self.format_to_uris(store, wid, tid, self.selected_files, True)
        self.to_cut_files = uris

    def copy_files(self):
        wid, tid, tab, icon_grid, store = self.get_current_state()
        uris = self.format_to_uris(store, wid, tid, self.selected_files, True)
        self.to_copy_files = uris

    def paste_files(self):
        wid, tid  = self.fm_controller.get_active_wid_and_tid()
        tab       = self.get_fm_window(wid).get_tab_by_id(tid)
        target    = f"{tab.get_current_directory()}"

        if self.to_copy_files:
            self.handle_files(self.to_copy_files, "copy", target)
        elif self.to_cut_files:
            self.handle_files(self.to_cut_files, "move", target)

    def delete_files(self):
        wid, tid, tab, icon_grid, store = self.get_current_state()
        uris     = self.format_to_uris(store, wid, tid, self.selected_files, True)
        response = None

        self.warning_alert.format_secondary_text(f"Do you really want to delete the {len(uris)} file(s)?")
        for uri in uris:
            file = Gio.File.new_for_path(uri)

            if not response:
                response = self.warning_alert.run()
                self.warning_alert.hide()
            if response == Gtk.ResponseType.YES:
                type = file.query_file_type(flags=Gio.FileQueryInfoFlags.NONE)

                if type == Gio.FileType.DIRECTORY:
                    tab.delete_file( file.get_path() )
                else:
                    file.delete(cancellable=None)
            else:
                break


    def trash_files(self):
        wid, tid, tab, icon_grid, store = self.get_current_state()
        uris      = self.format_to_uris(store, wid, tid, self.selected_files, True)
        for uri in uris:
            self.trashman.trash(uri, False)

    def restore_trash_files(self):
        wid, tid, tab, icon_grid, store = self.get_current_state()
        uris      = self.format_to_uris(store, wid, tid, self.selected_files, True)
        for uri in uris:
            self.trashman.restore(filename=uri.split("/")[-1], verbose=False)

    def empty_trash(self):
        self.trashman.empty(verbose=False)


    def create_files(self):
        fname_field = self.builder.get_object("context_menu_fname")
        file_name   = fname_field.get_text().strip()
        type        = self.builder.get_object("context_menu_type_toggle").get_state()

        wid, tid    = self.fm_controller.get_active_wid_and_tid()
        tab         = self.get_fm_window(wid).get_tab_by_id(tid)
        target      = f"{tab.get_current_directory()}"

        if file_name:
            path = f"{target}/{file_name}"

            if type == True:     # Create File
                self.handle_files([path], "create_file")
            else:                # Create Folder
                self.handle_files([path], "create_dir")

        self.hide_new_file_menu()

    def move_files(self, files, target):
        self.handle_files(files, "move", target)

    # NOTE: Gtk recommends using fail flow than pre check which is more
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
                if "file://" in path:
                    path = path.split("file://")[1]

                file = Gio.File.new_for_path(path)
                if _target_path:
                    if os.path.isdir(_target_path):
                        info    = file.query_info("standard::display-name", 0, cancellable=None)
                        _target = f"{_target_path}/{info.get_display_name()}"
                        _file   = Gio.File.new_for_path(_target)
                    else:
                        _file   = Gio.File.new_for_path(_target_path)
                else:
                    _file = Gio.File.new_for_path(path)


                if _file.query_exists():
                    if not overwrite_all and not rename_auto_all:
                        self.setup_exists_data(file, _file)
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
                            wid, tid = self.fm_controller.get_active_wid_and_tid()
                            tab      = self.get_fm_window(wid).get_tab_by_id(tid)
                            tab.delete_file( _file.get_path() )
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
                    wid, tid  = self.fm_controller.get_active_wid_and_tid()
                    tab       = self.get_fm_window(wid).get_tab_by_id(tid)
                    fPath     = file.get_path()
                    tPath     = target.get_path()
                    state     = True

                    if action == "copy":
                        tab.copy_file(fPath, tPath)
                    if action == "move" or action == "rename":
                        tab.move_file(fPath, tPath)
                else:
                    if action == "copy":
                        file.copy(target, flags=Gio.FileCopyFlags.BACKUP, cancellable=None)
                    if action == "move" or action == "rename":
                        file.move(target, flags=Gio.FileCopyFlags.BACKUP, cancellable=None)

            except GObject.GError as e:
                raise OSError(e)

        self.exists_file_rename_bttn.set_sensitive(False)


    def setup_exists_data(self, from_file, to_file):
        from_info             = from_file.query_info("standard::*,time::modified", 0, cancellable=None)
        to_info               = to_file.query_info("standard::*,time::modified", 0, cancellable=None)
        exists_file_diff_from = self.builder.get_object("exists_file_diff_from")
        exists_file_diff_to   = self.builder.get_object("exists_file_diff_to")
        exists_file_from      = self.builder.get_object("exists_file_from")
        exists_file_to        = self.builder.get_object("exists_file_to")
        from_date             = from_info.get_modification_date_time()
        to_date               = to_info.get_modification_date_time()
        from_size             = from_info.get_size()
        to_size               = to_info.get_size()

        exists_file_from.set_label(from_file.get_parent().get_path())
        exists_file_to.set_label(to_file.get_parent().get_path())
        self.exists_file_label.set_label(to_file.get_basename())
        self.exists_file_field.set_text(to_file.get_basename())

        # Returns: -1, 0 or 1 if dt1 is less than, equal to or greater than dt2.
        age       = GLib.DateTime.compare(from_date, to_date)
        age_text  = "( same time )"
        if age == -1:
            age_text = "older"
        if age == 1:
            age_text = "newer"

        size_text = "( same size )"
        if from_size < to_size:
            size_text = "smaller"
        if from_size > to_size:
            size_text = "larger"

        from_label_text = f"{age_text} & {size_text}"
        if age_text != "( same time )" or size_text != "( same size )":
            from_label_text = f"{from_date.format('%F %R')}     {self.sizeof_fmt(from_size)}     ( {from_size} bytes )  ( {age_text} & {size_text} )"
        to_label_text = f"{to_date.format('%F %R')}     {self.sizeof_fmt(to_size)}     ( {to_size} bytes )"

        exists_file_diff_from.set_text(from_label_text)
        exists_file_diff_to.set_text(to_label_text)


    def rename_proc(self, gio_file):
        full_path = gio_file.get_path()
        base_path = gio_file.get_parent().get_path()
        file_name = os.path.splitext(gio_file.get_basename())[0]
        extension = os.path.splitext(full_path)[-1]
        target    = Gio.File.new_for_path(full_path)
        start     = "-copy"

        if debug:
            print(f"Path:  {full_path}")
            print(f"Base Path:  {base_path}")
            print(f'Name:  {file_name}')
            print(f"Extension:  {extension}")

        i = 2
        while target.query_exists():
            try:
                value     = file_name[(file_name.find(start)+len(start)):]
                int(value)
                file_name = file_name.split(start)[0]
            except Exception as e:
                pass

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
