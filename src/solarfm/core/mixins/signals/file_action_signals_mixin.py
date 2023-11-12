# Python imports
import time

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import Gio


# Application imports



class FileActionSignalsMixin:
    """docstring for FileActionSignalsMixin"""

    def set_file_watcher(self, tab):
        if tab.get_dir_watcher():
            watcher = tab.get_dir_watcher()
            watcher.cancel()
            if settings_manager.is_debug():
                logger.debug(f"Watcher Is Cancelled:  {watcher.is_cancelled()}")

        cur_dir = tab.get_current_directory()

        dir_watcher  = Gio.File.new_for_path(cur_dir) \
                                .monitor_directory(Gio.FileMonitorFlags.WATCH_MOVES, Gio.Cancellable())

        wid = tab.get_wid()
        tid = tab.get_id()
        dir_watcher.connect("changed", self.dir_watch_updates, (f"{wid}|{tid}",))
        tab.set_dir_watcher(dir_watcher)

    # NOTE: Too lazy to impliment a proper update handler and so just regen store and update tab.
    #       Use a lock system to prevent too many update calls for certain instances but user can manually refresh if they have urgency
    def dir_watch_updates(self, file_monitor, file, other_file = None, eve_type = None, data = None):
        if eve_type in  [Gio.FileMonitorEvent.CREATED, Gio.FileMonitorEvent.DELETED,
                        Gio.FileMonitorEvent.RENAMED, Gio.FileMonitorEvent.MOVED_IN,
                        Gio.FileMonitorEvent.MOVED_OUT]:
            logger.debug(eve_type)

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
        icon_grid = self.builder.get_object(f"{wid}|{tid}|icon_grid", use_gtk = False)
        store     = icon_grid.get_model()
        _store, tab_widget_label = self.get_store_and_label_from_notebook(notebook, f"{wid}|{tid}")

        tab.load_directory()
        icon_grid.clear_and_set_new_store()
        self.load_store(tab, icon_grid.get_store())

        tab_widget_label.set_label(tab.get_end_of_path())
        state = self.get_current_state()
        if [wid, tid] in [state.wid, state.tid]:
            self.set_bottom_labels(tab)


    def do_file_search(self, widget, eve = None):
        if not self.ctrl_down and not self.shift_down and not self.alt_down:
            target    = widget.get_name()
            notebook  = self.builder.get_object(target)
            page      = notebook.get_current_page()
            nth_page  = notebook.get_nth_page(page)
            icon_grid = nth_page.get_children()[0]

            wid, tid  = icon_grid.get_name().split("|")
            tab       = self.get_fm_window(wid).get_tab_by_id(tid)
            query     = widget.get_text().lower()

            icon_grid.unselect_all()
            for i, file in enumerate(tab.get_files()):
                if query and query in file[0].lower():
                    path = Gtk.TreePath().new_from_indices([i])
                    icon_grid.select_path(path)

            items = icon_grid.get_selected_items()
            if len(items) > 0:
                icon_grid.scroll_to_path(items[0], False, 0.5, 0.5)
