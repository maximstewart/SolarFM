# Python imports
import os
import traceback
import threading
import subprocess
import time
from os.path import isdir

# Lib imports
import gi

gi.require_version("Gtk", "3.0")
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import Gdk
from gi.repository import GdkPixbuf
from gi.repository import Gio


# Application imports




class FileView(Gtk.Box):
    """docstring for FileView."""

    def __init__(self, _icon = None, _label = None):
        super(FileView, self).__init__()
        self.icon  = None
        self.label = _label

        self.label.set_line_wrap(True)
        self.label.set_selectable(True)
        self.label.set_max_width_chars(20)
        self.label.set_justify(2)
        self.label.set_line_wrap_mode(2)

        self.add(self.label)
        self.set_orientation(1)

        self.show_all()

    def set_img(self, img):
        self.icon  = img
        self.add(img)
        self.reorder_child(self.icon, 0)



class IconViewSignalsMixin:
    """docstring for WidgetMixin"""

    def load_store(self):
        self._clear_children(self)
        self.search_filter("")

        dir   = self.tab_state.get_current_directory()
        files = self.tab_state.get_files()

        for i, file in enumerate(files):
            label = Gtk.Label(label=file[0])
            child = Gtk.FlowBoxChild()
            child.set_name(file[0])

            file_view = FileView(_label=label)
            child.add( file_view )
            self.add(child)
            self.create_icon(file_view, dir, file[0])

    @threaded
    def create_icon(self, file_view, dir, file):
        icon = self.tab_state.create_icon(dir, file)
        GLib.idle_add(self.update_store, *(file_view, icon, dir, file,))

    def update_store(self, file_view, icon,  dir, file):
        if not icon:
            path = f"{dir}/{file}"
            icon = self.get_system_thumbnail(path, self.tab_state.sys_icon_wh[0])

        if not icon:
            icon = GdkPixbuf.Pixbuf.new_from_file(self.tab_state.DEFAULT_ICON)

        img   = Gtk.Image.new_from_pixbuf(icon)
        img.show()
        file_view.set_img(img)
        self.show_all()


    def get_system_thumbnail(self, filename, size):
        try:
            gio_file  = Gio.File.new_for_path(filename)
            info      = gio_file.query_info('standard::icon' , 0, None)
            icon      = info.get_icon().get_names()[0]
            icon_path = self.icon_theme.lookup_icon(icon , size , 0).get_filename()

            return GdkPixbuf.Pixbuf.new_from_file(icon_path)
        except Exception:
            ...

        return None


    def icon_double_click(self, icons_grid, item, data=None):
        try:
            file_view  = item.get_children()[0]
            file_name  = file_view.label.get_label()
            dir        = self.tab_state.get_current_directory()
            file       = f"{dir}/{file_name}"

            if isdir(file):
                self.tab_state.set_path(file)
                self.load_store()
                self._emmit_signal_to_file_view('update-tab-title')
            else:
                event_system.emit("open_files", (self, file))
        except Exception as e:
            traceback.print_exc()


    def go_up_dir(self):
        self.tab_state.pop_from_path()
        self.load_store()
        self._emmit_signal_to_file_view('update-tab-title')

    def go_home_dir(self):
        self.tab_state.set_to_home()
        self.load_store()
        self._emmit_signal_to_file_view('update-tab-title')

    def go_to_path(self, path):
        self.tab_state.set_path(path)
        self.load_store()
        self._emmit_signal_to_file_view('update-tab-title')

    def refresh_dir(self):
        self.tab_state.load_directory()
        self.load_store()

    # def on_drag_set(self, icons_grid, drag_context, data, info, time):
    #     action    = icons_grid.get_name()
    #     wid, tid  = action.split("|")
    #     store     = icons_grid.get_model()
    #     treePaths = icons_grid.get_selected_items()
    #     # NOTE: Need URIs as URI format for DnD to work. Will strip 'file://'
    #     # further down call chain when doing internal fm stuff.
    #     uris      = self.format_to_uris(store, wid, tid, treePaths)
    #     uris_text = '\n'.join(uris)
    #
    #     data.set_uris(uris)
    #     data.set_text(uris_text, -1)
    #
    # def on_drag_motion(self, icons_grid, drag_context, x, y, data):
    #     current   = '|'.join(self.fm_controller.get_active_wid_and_tid())
    #     target    = icons_grid.get_name()
    #     wid, tid  = target.split("|")
    #     store     = icons_grid.get_model()
    #     treePath  = icons_grid.get_drag_dest_item().path
    #
    #     if treePath:
    #         uri = self.format_to_uris(store, wid, tid, treePath)[0].replace("file://", "")
    #         self.override_drop_dest = uri if isdir(uri) else None
    #
    #     if target not in current:
    #         self.fm_controller.set_wid_and_tid(wid, tid)
    #
    #
    # def on_drag_data_received(self, widget, drag_context, x, y, data, info, time):
    #     if info == 80:
    #         wid, tid  = self.fm_controller.get_active_wid_and_tid()
    #         notebook  = self.builder.get_object(f"window_{wid}")
    #         store, tab_label = self.get_store_and_label_from_notebook(notebook, f"{wid}|{tid}")
    #         tab       = self.get_fm_window(wid).get_tab_by_id(tid)
    #
    #         uris = data.get_uris()
    #         dest = f"{tab.get_current_directory()}" if not self.override_drop_dest else self.override_drop_dest
    #         if len(uris) == 0:
    #             uris = data.get_text().split("\n")
    #
    #         from_uri = '/'.join(uris[0].replace("file://", "").split("/")[:-1])
    #         if from_uri != dest:
    #             self.move_files(uris, dest)
