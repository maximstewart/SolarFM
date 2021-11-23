# Python imports
import os, threading, subprocess

# Lib imports
import gi

gi.require_version("Gtk", "3.0")
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import Gio
from gi.repository import GdkPixbuf

# Application imports


def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()
    return wrapper



class WidgetMixin:

    def load_store(self, view, store, save_state=False):
        store.clear()
        dir   = view.get_current_directory()
        files = view.get_files()

        icon = GdkPixbuf.Pixbuf.new_from_file(view.DEFAULT_ICON)
        for i, file in enumerate(files):
            store.append([icon, file[0]])
            self.create_icon(i, view, store, dir, file[0])

        # NOTE: Not likely called often from here but it could be useful
        if save_state:
            self.window_controller.save_state()

    @threaded
    def create_icon(self, i, view, store, dir, file):
        icon  = view.create_icon(dir, file)
        fpath = dir + "/" + file
        GLib.idle_add(self.update_store, (i, store, icon, view, fpath,))

    def update_store(self, item):
        i, store, icon, view, fpath = item
        itr  = store.get_iter(i)

        if not icon:
            icon = self.get_system_thumbnail(fpath, view.SYS_ICON_WH[0])
            if not icon:
                if fpath.endswith(".gif"):
                    icon = GdkPixbuf.PixbufAnimation.get_static_image(fpath)
                else:
                    icon = GdkPixbuf.Pixbuf.new_from_file(view.DEFAULT_ICON)

        store.set_value(itr, 0, icon)


    def get_system_thumbnail(self, filename, size):
        try:
            if os.path.exists(filename):
                gioFile   = Gio.File.new_for_path(filename)
                info      = gioFile.query_info('standard::icon' , 0, Gio.Cancellable())
                icon      = info.get_icon().get_names()[0]
                iconTheme = Gtk.IconTheme.get_default()
                iconData  = iconTheme.lookup_icon(icon , size , 0)
                if iconData:
                    iconPath  = iconData.get_filename()
                    return GdkPixbuf.Pixbuf.new_from_file(iconPath)
                else:
                    return None
            else:
                return None
        except Exception as e:
            print("System icon generation issue:")
            print( repr(e) )
            return None




    def create_tab_widget(self, view):
        tab   = Gtk.Box()
        label = Gtk.Label()
        tid   = Gtk.Label()
        close = Gtk.Button()
        icon  = Gtk.Image(stock=Gtk.STOCK_CLOSE)

        label.set_label(f"{view.get_end_of_path()}")
        label.set_width_chars(25)
        label.set_max_width_chars(64)
        label.set_ellipsize(2)  #PANGO_ELLIPSIZE_MIDDLE
        tid.set_label(f"{view.id}")

        close.add(icon)
        tab.add(label)
        tab.add(close)
        tab.add(tid)

        close.connect("released", self.close_tab)
        tab.show_all()
        tid.hide()
        return tab

    def create_grid_iconview_widget(self, view, wid):
        scroll = Gtk.ScrolledWindow()
        grid   = Gtk.IconView()
        store  = Gtk.ListStore(GdkPixbuf.Pixbuf, str)

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

        grid.connect("button_release_event", self.grid_icon_single_left_click)
        grid.connect("item-activated", self.grid_icon_double_left_click)
        grid.connect("selection-changed", self.grid_set_selected_items)
        grid.connect("drag-data-get", self.grid_on_drag_set)
        grid.connect("drag-data-received", self.grid_on_drag_data_received)
        grid.connect("drag-motion", self.grid_on_drag_motion)

        URI_TARGET_TYPE  = 80
        uri_target       = Gtk.TargetEntry.new('text/uri-list', Gtk.TargetFlags(0), URI_TARGET_TYPE)
        targets          = [ uri_target ]
        action           = Gdk.DragAction.COPY
        grid.enable_model_drag_dest(targets, action)
        grid.enable_model_drag_source(0, targets, action)

        grid.show_all()
        scroll.add(grid)
        grid.set_name(f"{wid}|{view.id}")
        self.builder.expose_object(f"{wid}|{view.id}|iconview", grid)
        self.builder.expose_object(f"{wid}|{view.id}", scroll)
        return scroll, store

    def create_grid_treeview_widget(self, view, wid):
        scroll = Gtk.ScrolledWindow()
        grid   = Gtk.TreeView()
        store  = Gtk.ListStore(GdkPixbuf.Pixbuf, str)
        # store  = Gtk.TreeStore(GdkPixbuf.Pixbuf, str)
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

        grid.connect("button_release_event", self.grid_icon_single_left_click)
        grid.connect("row-activated", self.grid_icon_double_left_click)
        grid.connect("drag-data-get", self.grid_on_drag_set)
        grid.connect("drag-data-received", self.grid_on_drag_data_received)
        grid.connect("drag-motion", self.grid_on_drag_motion)

        URI_TARGET_TYPE  = 80
        uri_target       = Gtk.TargetEntry.new('text/uri-list', Gtk.TargetFlags(0), URI_TARGET_TYPE)
        targets          = [ uri_target ]
        action           = Gdk.DragAction.COPY
        grid.enable_model_drag_dest(targets, action)
        grid.enable_model_drag_source(0, targets, action)


        grid.show_all()
        scroll.add(grid)
        grid.set_name(f"{wid}|{view.id}")
        grid.columns_autosize()
        self.builder.expose_object(f"{wid}|{view.id}", scroll)
        return scroll, store


    def get_store_and_label_from_notebook(self, notebook, _name):
        icon_view = None
        tab_label = None
        store     = None

        for obj in notebook.get_children():
            icon_view = obj.get_children()[0]
            name      =  icon_view.get_name()
            if name == _name:
                store = icon_view.get_model()
                tab_label = notebook.get_tab_label(obj).get_children()[0]

        return store, tab_label
