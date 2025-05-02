# Python imports
import os

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GObject
from gi.repository import Gio

# Application imports
from ..widgets.io_widget import IOWidget


class HandlerMixinException(Exception):
    ...



class HandlerMixin:
    """docstring for HandlerMixin"""

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
                    if file.get_parent().get_path() == _target_path:
                        raise HandlerMixinException("Parent dir of target and file locations are the same! Won't copy or move!")

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
                        event_system.emit("setup_exists_data", (file, _file))
                        response = event_system.emit_and_await("show_exists_page")

                    if response == "overwrite_all":
                        overwrite_all   = True
                    if response == "rename_auto_all":
                        rename_auto_all = True

                    if response == "rename":
                        base_path = _file.get_parent().get_path()
                        new_name  = self._builder.get_object("exists_file_field").get_text().strip()
                        rfPath    = f"{base_path}/{new_name}"
                        _file     = Gio.File.new_for_path(rfPath)

                    if response == "rename_auto" or rename_auto_all:
                        _file = self.rename_proc(_file)

                    if response == "overwrite" or overwrite_all:
                        type      = _file.query_file_type(flags=Gio.FileQueryInfoFlags.NONE)

                        if type == Gio.FileType.DIRECTORY:
                            state = event_system.emit_and_await("get_current_state")
                            state.tab.delete_file( _file.get_path() )
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
                    state     = event_system.emit_and_await("get_current_state")
                    tab       = state.tab
                    fPath     = file.get_path()
                    tPath     = target.get_path()
                    state     = True

                    if action == "copy":
                        tab.copy_file(fPath, tPath)
                    if action == "move" or action == "rename":
                        tab.move_file(fPath, tPath)
                else:
                    io_widget = IOWidget(action, file)
                    io_list   = self._builder.get_object("io_list")

                    io_list.add(io_widget)
                    io_list.show_all()

                    if action == "copy":
                        file.copy_async(target,
                                        Gio.FileCopyFlags.BACKUP,
                                        45,
                                        io_widget.cancle_eve,
                                        io_widget.update_progress,
                                        io_widget.finish_callback)

                    if action == "move" or action == "rename":
                        file.move_async(target,
                                        Gio.FileCopyFlags.BACKUP,
                                        45,
                                        io_widget.cancle_eve,
                                        None,
                                        io_widget.finish_callback)

                        io_widget = None
                        io_list   = None

            except GObject.GError as e:
                raise OSError(e)

        self._builder.get_object("exists_file_rename_bttn").set_sensitive(False)

    def rename_proc(self, gio_file):
        full_path = gio_file.get_path()
        base_path = gio_file.get_parent().get_path()
        file_name = os.path.splitext(gio_file.get_basename())[0]
        extension = os.path.splitext(full_path)[-1]
        target    = Gio.File.new_for_path(full_path)
        start     = "-copy"

        if settings_manager.is_debug():
            logger.debug(f"Path:  {full_path}")
            logger.debug(f"Base Path:  {base_path}")
            logger.debug(f'Name:  {file_name}')
            logger.debug(f"Extension:  {extension}")

        i = 2
        while target.query_exists():
            try:
                value     = file_name[(file_name.find(start)+len(start)):]
                int(value)
                file_name = file_name.split(start)[0]
            except HandlerMixinException as e:
                pass

            target = Gio.File.new_for_path(f"{base_path}/{file_name}-copy{i}{extension}")
            i += 1

        return target