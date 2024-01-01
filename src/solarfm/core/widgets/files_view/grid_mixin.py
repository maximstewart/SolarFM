# Python imports
import asyncio

# Lib imports
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import Gio

# Application imports
from ...widgets.tab_header_widget import TabHeaderWidget
from ...widgets.icon_grid_widget import IconGridWidget
from ...widgets.icon_tree_widget import IconTreeWidget



class GridMixin:
    """docstring for GridMixin"""

    def load_store(self, tab, store, save_state = False, use_generator = False):
        # dir      = tab.get_current_directory()
        # file     = Gio.File.new_for_path(dir)
        # dir_list = Gtk.DirectoryList.new("standard::*", file)
        # store.set(dir_list)

        # file  = Gio.File.new_for_path(dir)
        # for file in file.enumerate_children("standard::*", Gio.FILE_ATTRIBUTE_STANDARD_NAME, None):
        #     store.append(file)

        # return


        dir   = tab.get_current_directory()
        files = tab.get_files()

        for file in files:
            store.append([None, file[0]])

        Gtk.main_iteration()
        GLib.Thread("", self.generate_icons, tab, store, dir, files)

        # NOTE: Not likely called often from here but it could be useful
        if save_state and not trace_debug:
            self.fm_controller.save_state()


    def generate_icons(self, tab, store, dir, files):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            loop.create_task( self.create_icons(tab, store, dir, files) )
        else:
            asyncio.run( self.create_icons(tab, store, dir, files) )

    async def create_icons(self, tab, store, dir, files):
        icons = [self.get_icon(tab, dir, file[0]) for file in files]
        data  = await asyncio.gather(*icons)
        tasks = [self.update_store(i, store, icon) for i, icon in enumerate(data)]
        await asyncio.gather(*tasks)

        GLib.idle_add(Gtk.main_iteration)

    async def update_store(self, i, store, icon):
        itr  = store.get_iter(i)
        GLib.idle_add(self.insert_store, store, itr, icon)

    def insert_store(self, store, itr, icon):
        store.set_value(itr, 0, icon)
        # Note:  If the function returns GLib.SOURCE_REMOVE or False it is automatically removed from the list of event sources and will not be called again.
        return False

    async def get_icon(self, tab, dir, file):
        return tab.create_icon(dir, file)

    def create_tab_widget(self, tab):
        return TabHeaderWidget(tab, self.close_tab)

    def create_scroll_and_store(self, tab, wid, use_tree_view = False):
        scroll = Gtk.ScrolledWindow()

        if not use_tree_view:
            grid = self.create_icon_grid_widget()
        else:
            # TODO: Fix global logic to make the below work too
            grid = self.create_icon_tree_widget()

        scroll.add(grid)
        scroll.set_name(f"{wid}|{tab.get_id()}")
        grid.set_name(f"{wid}|{tab.get_id()}")
        self.builder.expose_object(f"{wid}|{tab.get_id()}|icon_grid", grid, use_gtk = False)
        self.builder.expose_object(f"{wid}|{tab.get_id()}", scroll, use_gtk = False)

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