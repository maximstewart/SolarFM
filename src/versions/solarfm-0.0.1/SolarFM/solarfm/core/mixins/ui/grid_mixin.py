# Python imports
import os, threading, subprocess, time

# Lib imports
import gi

gi.require_version("Gtk", "3.0")
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk, GLib, Gio, GdkPixbuf

# Application imports


def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs, daemon=True).start()
    return wrapper




# NOTE: Consider trying to use Gtk.TreeView with css that turns it into a grid...
# Can possibly use this to dynamicly load icons instead...
class Icon(Gtk.HBox):
    def __init__(self, tab, dir, file):
        super(Icon, self).__init__()

        self.load_icon(tab, dir, file)

    @threaded
    def load_icon(self, tab, dir, file):
        icon = tab.create_icon(dir, file)

        if not icon:
            path = f"{dir}/{file}"
            icon = self.get_system_thumbnail(path, tab.sys_icon_wh[0])

        if not icon:
            icon = GdkPixbuf.Pixbuf.new_from_file(tab.DEFAULT_ICON)

        self.add(Gtk.Image.new_from_pixbuf(icon))
        self.show_all()

    def get_system_thumbnail(self, file, size):
        try:
            gio_file  = Gio.File.new_for_path(file)
            info      = gio_file.query_info('standard::icon' , 0, None)
            icon      = info.get_icon().get_names()[0]
            icon_path = self.icon_theme.lookup_icon(icon , size , 0).get_filename()
            return GdkPixbuf.Pixbuf.new_from_file(icon_path)
        except Exception as e:
            return None


class GridMixin:
    """docstring for WidgetMixin"""

    def load_store(self, tab, store, save_state=False):
        store.clear()
        dir   = tab.get_current_directory()
        files = tab.get_files()

        for file in files:
            store.append([None, file[0]])

        for i, file in enumerate(files):
            self.create_icon(i, tab, store, dir, file[0])

        # NOTE: Not likely called often from here but it could be useful
        if save_state:
            self.fm_controller.save_state()

    @threaded
    def create_icon(self, i, tab, store, dir, file):
        icon = tab.create_icon(dir, file)
        GLib.idle_add(self.update_store, *(i, store, icon, tab, dir, file,))

    def update_store(self, i, store, icon, tab, dir, file):
        if not icon:
            path = f"{dir}/{file}"
            icon = self.get_system_thumbnail(path, tab.sys_icon_wh[0])

        if not icon:
            icon = GdkPixbuf.Pixbuf.new_from_file(tab.DEFAULT_ICON)

        itr = store.get_iter(i)
        store.set_value(itr, 0, icon)

    def get_system_thumbnail(self, filename, size):
        try:
            gio_file  = Gio.File.new_for_path(filename)
            info      = gio_file.query_info('standard::icon' , 0, None)
            icon      = info.get_icon().get_names()[0]
            icon_path = self.icon_theme.lookup_icon(icon , size , 0).get_filename()
            return GdkPixbuf.Pixbuf.new_from_file(icon_path)
        except Exception as e:
            return None


    def create_tab_widget(self, tab):
        tab_widget = Gtk.ButtonBox()
        label = Gtk.Label()
        tid   = Gtk.Label()
        close = Gtk.Button()
        icon  = Gtk.Image(stock=Gtk.STOCK_CLOSE)

        label.set_label(f"{tab.get_end_of_path()}")
        label.set_width_chars(len(tab.get_end_of_path()))
        label.set_xalign(0.0)
        tid.set_label(f"{tab.get_id()}")

        close.add(icon)
        tab_widget.add(label)
        tab_widget.add(close)
        tab_widget.add(tid)

        close.connect("released", self.close_tab)
        tab_widget.show_all()
        tid.hide()
        return tab_widget

    def create_scroll_and_store(self, tab, wid, use_tree_view=False):
        if not use_tree_view:
            scroll, store = self.create_icon_grid_widget(tab, wid)
        else:
            # TODO: Fix global logic to make the below work too
            scroll, store = self.create_icon_tree_widget(tab, wid)

        return scroll, store

    def create_icon_grid_widget(self, tab, wid):
        scroll = Gtk.ScrolledWindow()
        grid   = Gtk.IconView()
        store  = Gtk.ListStore(GdkPixbuf.Pixbuf or GdkPixbuf.PixbufAnimation or None, str or None)

        grid.set_model(store)
        grid.set_pixbuf_column(0)
        grid.set_text_column(1)

        grid.set_item_orientation(1)
        grid.set_selection_mode(3)
        grid.set_item_width(96)
        grid.set_item_padding(8)
        grid.set_margin(12)
        grid.set_row_spacing(18)
        grid.set_columns(-1)
        grid.set_spacing(12)
        grid.set_column_spacing(18)

        grid.connect("button_release_event", self.grid_icon_single_click)
        grid.connect("item-activated",       self.grid_icon_double_click)
        grid.connect("selection-changed",    self.grid_set_selected_items)
        grid.connect("drag-data-get",        self.grid_on_drag_set)
        grid.connect("drag-data-received",   self.grid_on_drag_data_received)
        grid.connect("drag-motion",          self.grid_on_drag_motion)

        URI_TARGET_TYPE  = 80
        uri_target       = Gtk.TargetEntry.new('text/uri-list', Gtk.TargetFlags(0), URI_TARGET_TYPE)
        targets          = [ uri_target ]
        action           = Gdk.DragAction.COPY
        grid.enable_model_drag_dest(targets, action)
        grid.enable_model_drag_source(0, targets, action)

        grid.show_all()
        scroll.add(grid)
        grid.set_name(f"{wid}|{tab.get_id()}")
        scroll.set_name(f"{wid}|{tab.get_id()}")
        self.builder.expose_object(f"{wid}|{tab.get_id()}|icon_grid", grid)
        self.builder.expose_object(f"{wid}|{tab.get_id()}", scroll)
        return scroll, store

    def create_icon_tree_widget(self, tab, wid):
        scroll = Gtk.ScrolledWindow()
        grid   = Gtk.TreeView()
        store  = Gtk.TreeStore(GdkPixbuf.Pixbuf or GdkPixbuf.PixbufAnimation or None, str or None)
        column = Gtk.TreeViewColumn("Icons")
        icon   = Gtk.CellRendererPixbuf()
        name   = Gtk.CellRendererText()
        selec  = grid.get_selection()

        grid.set_model(store)
        selec.set_mode(3)
        column.pack_start(icon, False)
        column.pack_start(name, True)
        column.add_attribute(icon, "pixbuf", 0)
        column.add_attribute(name, "text", 1)
        column.set_expand(False)
        column.set_sizing(2)
        column.set_min_width(120)
        column.set_max_width(74)

        grid.append_column(column)
        grid.set_search_column(1)
        grid.set_rubber_banding(True)
        grid.set_headers_visible(False)
        grid.set_enable_tree_lines(False)

        grid.connect("button_release_event", self.grid_icon_single_click)
        grid.connect("row-activated",        self.grid_icon_double_click)
        grid.connect("drag-data-get",        self.grid_on_drag_set)
        grid.connect("drag-data-received",   self.grid_on_drag_data_received)
        grid.connect("drag-motion",          self.grid_on_drag_motion)

        URI_TARGET_TYPE  = 80
        uri_target       = Gtk.TargetEntry.new('text/uri-list', Gtk.TargetFlags(0), URI_TARGET_TYPE)
        targets          = [ uri_target ]
        action           = Gdk.DragAction.COPY
        grid.enable_model_drag_dest(targets, action)
        grid.enable_model_drag_source(0, targets, action)

        grid.show_all()
        scroll.add(grid)
        grid.set_name(f"{wid}|{tab.get_id()}")
        scroll.set_name(f"{wid}|{tab.get_id()}")
        self.builder.expose_object(f"{wid}|{tab.get_id()}|icon_grid", grid)
        self.builder.expose_object(f"{wid}|{tab.get_id()}", scroll)
        grid.columns_autosize()

        self.builder.expose_object(f"{wid}|{tab.get_id()}", scroll)
        return scroll, store


    def get_store_and_label_from_notebook(self, notebook, _name):
        icon_grid = None
        tab_label = None
        store     = None

        for obj in notebook.get_children():
            icon_grid = obj.get_children()[0]
            name      = icon_grid.get_name()
            if name == _name:
                store     = icon_grid.get_model()
                tab_label = notebook.get_tab_label(obj).get_children()[0]

        return store, tab_label
