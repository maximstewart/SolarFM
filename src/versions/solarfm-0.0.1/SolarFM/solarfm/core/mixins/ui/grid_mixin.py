# Python imports

# Lib imports
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import GLib

# Application imports
from ...widgets.tab_header_widget import TabHeaderWidget
from ...widgets.icon_grid_widget import IconGridWidget
from ...widgets.icon_tree_widget import IconTreeWidget




class GridMixin:
    """docstring for GridMixin"""

    def load_store(self, tab, store, save_state=False):
        store.clear()
        dir   = tab.get_current_directory()
        files = tab.get_files()

        for file in files:
            store.append([None, file[0]])

        self.load_icons(tab, store, dir, files)

        # NOTE: Not likely called often from here but it could be useful
        if save_state and not trace_debug:
            self.fm_controller.save_state()


    @threaded
    def load_icons(self, tab, store, dir, files):
        for i, file in enumerate(files):
            self.create_icon(i, tab, store, dir, file[0])

    def create_icon(self, i, tab, store, dir, file):
        icon = tab.create_icon(dir, file)
        GLib.idle_add(self.update_store, *(i, store, icon,))

    def update_store(self, i, store, icon):
        itr = store.get_iter(i)
        store.set_value(itr, 0, icon)


    def create_tab_widget(self, tab):
        return TabHeaderWidget(tab, self.close_tab)

    def create_scroll_and_store(self, tab, wid, use_tree_view=False):
        scroll = Gtk.ScrolledWindow()

        if not use_tree_view:
            grid = self.create_icon_grid_widget()
        else:
            # TODO: Fix global logic to make the below work too
            grid = self.create_icon_tree_widget()

        scroll.add(grid)
        scroll.set_name(f"{wid}|{tab.get_id()}")
        grid.set_name(f"{wid}|{tab.get_id()}")
        self.builder.expose_object(f"{wid}|{tab.get_id()}|icon_grid", grid)
        self.builder.expose_object(f"{wid}|{tab.get_id()}", scroll)

        return scroll, grid.get_store()

    def create_icon_grid_widget(self):
        grid = IconGridWidget()
        grid._setup_additional_signals(
            self.grid_icon_single_click,
            self.grid_icon_double_click,
            self.grid_set_selected_items,
            self.grid_on_drag_set,
            self.grid_on_drag_data_received,
            self.grid_on_drag_motion
        )

        return grid

    def create_icon_tree_widget(self):
        grid = IconTreeWidget()
        grid._setup_additional_signals(
            self.grid_icon_single_click,
            self.grid_icon_double_click,
            self.grid_on_drag_set,
            self.grid_on_drag_data_received,
            self.grid_on_drag_motion
        )

        grid.columns_autosize()
        return grid

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
