# Python imports
import threading, subprocess

# Lib imports
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import GdkPixbuf

# Application imports


def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()
    return wrapper



class WidgetMixin:
    # This feels ugly but I don't see a better option than itterating over the list.
    # @threaded
    # def load_store(self, view, store, save_state=True):
    #     store.clear()
    #     files = view.get_pixbuf_icon_str_combo()
    #
    #     for data in files:
    #         store.append(data)
    #
    #     if save_state:
    #         self.window_controller.save_state()




    @threaded
    def load_store(self, view, store, save_state=True):
        store.clear()
        dir   = view.get_current_directory()
        files = view.get_files()
        for i, file in enumerate(files):
            icon = Gtk.Image.new_from_file(view.DEFAULT_ICON).get_pixbuf()
            store.append([icon, file[0]])
            try:
                self.create_icon(i, view, store, dir, file[0])
            except Exception as e:
                pass

        if save_state:
            self.window_controller.save_state()

    @threaded
    def create_icon(self, i, view, store, dir, file):
        GLib.idle_add(self.update_store, (i, view, store, dir, file,))

    def update_store(self, item):
        i, view, store, dir, file = item
        icon = view.create_icon(dir, file).get_pixbuf()
        itr  = store.get_iter(i)
        store.set_value(itr, 0, icon)




    def create_tab_widget(self, view):
        tab   = Gtk.Box()
        label = Gtk.Label()
        tid   = Gtk.Label()
        close = Gtk.EventBox()
        icon  = Gtk.Image(stock=Gtk.STOCK_CLOSE)

        label.set_label(f"{view.get_end_of_path()}")
        tid.set_label(f"{view.id}")

        close.add(icon)
        tab.add(label)
        tab.add(close)
        tab.add(tid)

        close.connect("button_release_event", self.close_tab)
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

        grid.set_item_orientation(0)
        grid.set_selection_mode(3)
        grid.set_item_width(152)
        grid.set_item_padding(2)
        grid.set_margin(2)
        grid.set_row_spacing(2)
        grid.set_columns(-1)
        grid.set_spacing(1)
        grid.set_column_spacing(2)

        grid.connect("button_release_event", self.icon_single_click)
        grid.connect("item-activated", self.icon_double_left_click)

        grid.show_all()
        scroll.add(grid)
        grid.set_name(f"{wid}|{view.id}")
        return scroll, store

    def create_grid_treeview_widget(self, view, wid):
        scroll = Gtk.ScrolledWindow()
        grid   = Gtk.TreeView()
        store  = Gtk.ListStore(GdkPixbuf.Pixbuf, str)
        column = Gtk.TreeViewColumn("Icons")
        icon   = Gtk.CellRendererPixbuf()
        name   = Gtk.CellRendererText()

        grid.set_model(store)
        column.pack_start(icon, False)
        column.pack_start(name, True)
        column.add_attribute(icon, "pixbuf", 0)
        column.add_attribute(name, "text", 1)
        column.set_expand(True)

        grid.append_column(column)
        grid.set_search_column(1)
        grid.set_rubber_banding(True)
        grid.set_headers_visible(False)
        grid.set_enable_tree_lines(False)
        grid.set_visible(True)

        # grid.connect("button_release_event", self.icon_single_click)
        # grid.connect("item-activated", self.icon_double_left_click)

        column.set_visible(True)
        icon.set_visible(True)
        name.set_visible(True)

        grid.show_all()
        scroll.add(grid)
        grid.set_name(f"{wid}|{view.id}")
        return scroll, store




    def on_tab_switch_update(self, notebook, content=None, index=None):
        wid, tid   = content.get_children()[0].get_name().split("|")
        self.window_controller.set_active_data(wid, tid)
        self.set_path_text(wid, tid)

    def set_path_text(self, wid, tid):
        path_entry = self.builder.get_object("path_entry")
        view       = self.get_fm_window(wid).get_view_by_id(tid)
        path_entry.set_text(view.get_current_directory())

    def get_tab_id_from_widget(self, tab_box):
        tid = tab_box.get_children()[2]
        return tid.get_text()

    def get_tab_label_widget_from_widget(self, notebook, widget):
        return notebook.get_tab_label(widget.get_parent()).get_children()[0]

    def get_icon_view_and_label_from_notebook(self, notebook, _name):
        icon_view = None
        tab_label = None

        for obj in notebook.get_children():
            icon_view = obj.get_children()[0]
            name      =  icon_view.get_name()
            if name == _name:
                tab_label = notebook.get_tab_label(obj).get_children()[0]

        return icon_view, tab_label
