# Python imports
import os
import gc
import time

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GLib

# Application imports
from .grid_mixin import GridMixin



class TabMixin(GridMixin):
    """docstring for TabMixin"""

    def create_tab(self, wid: int = None, tid: int = None, path: str = None):
        if not wid:
            wid, tid = self.fm_controller.get_active_wid_and_tid()

        notebook    = self.builder.get_object(f"window_{wid}")
        path_entry  = self.builder.get_object(f"path_entry")
        tab         = self.fm_controller.add_tab_for_window_by_nickname(f"window_{wid}")
        tab.logger  = logger

        tab.set_wid(wid)
        if not path:
            if wid and tid:
                _tab = self.get_fm_window(wid).get_tab_by_id(tid)
                tab.set_path(_tab.get_current_directory())
        else:
            tab.set_path(path)

        tab_widget    = self.get_tab_widget(tab)
        scroll, store = self.create_scroll_and_store(tab, wid)
        index         = notebook.append_page(scroll, tab_widget)
        notebook.set_tab_detachable(scroll, True)
        notebook.set_tab_reorderable(scroll, True)

        self.fm_controller.set_wid_and_tid(wid, tab.get_id())
        # path_entry.set_text(tab.get_current_directory())
        event_system.emit("go_to_path", (tab.get_current_directory(),)) # NOTE: Not efficent if I understand how
        notebook.show_all()
        notebook.set_current_page(index)

        ctx = notebook.get_style_context()
        ctx.add_class("notebook-unselected-focus")
        self.load_store(tab, store)
        event_system.emit("set_window_title", (tab.get_current_directory(),))
        self.set_file_watcher(tab)

        tab_widget    = None
        scroll, store = None, None
        index         = None
        notebook      = None
        path_entry    = None
        tab           = None
        ctx           = None


    def get_tab_widget(self, tab):
        tab_widget     = self.create_tab_widget()
        tab_widget.tab = tab

        tab_widget.label.set_label(f"{tab.get_end_of_path()}")
        tab_widget.label.set_width_chars(len(tab.get_end_of_path()))

        return tab_widget

    def close_tab(self, button, eve = None):
        notebook = button.get_parent().get_parent()
        if notebook.get_n_pages() == 1:
            notebook = None
            return

        tab_box   = button.get_parent()
        wid       = int(notebook.get_name()[-1])
        tid       = self.get_id_from_tab_box(tab_box)
        scroll    = self.builder.get_object(f"{wid}|{tid}", use_gtk = False)
        icon_grid = scroll.get_children()[0]
        store     = icon_grid.get_store()
        tab       = self.get_fm_window(wid).get_tab_by_id(tid)
        watcher   = tab.get_dir_watcher()

        watcher.cancel()
        self.get_fm_window(wid).delete_tab_by_id(tid)

        self.builder.dereference_object(f"{wid}|{tid}|icon_grid")
        self.builder.dereference_object(f"{wid}|{tid}")

        iter = store.get_iter_first()
        while iter:
            next_iter = store.iter_next(iter)
            store.unref_node(iter)
            iter = next_iter

        store.clear()
        store.run_dispose()

        icon_grid.set_model(None)
        icon_grid.run_dispose()
        scroll.run_dispose()
        tab_box.run_dispose()

        iter      = None
        wid, tid  = None, None
        store     = None
        icon_grid = None
        scroll    = None
        tab_box   = None
        watcher   = None
        tab       = None
        notebook  = None

        if not settings_manager.is_trace_debug():
            self.fm_controller.save_state()

        self.set_window_title()
        gc.collect()

    # NOTE: Not actually getting called even tho set in the glade file...
    def on_tab_dnded(self, notebook, page, x, y):
        ...

    def on_tab_reorder(self, child, page_num, new_index):
        wid, tid = page_num.get_name().split("|")
        window   = self.get_fm_window(wid)
        tab      = None

        for i, tab in enumerate(window.get_all_tabs()):
            if tab.get_id() == tid:
                _tab    = window.get_tab_by_id(tid)
                watcher = _tab.get_dir_watcher()
                watcher.cancel()
                window.get_all_tabs().insert(new_index, window.get_all_tabs().pop(i))

        tab = window.get_tab_by_id(tid)
        self.set_file_watcher(tab)
        if not settings_manager.is_trace_debug():
            self.fm_controller.save_state()

        wid, tid = None, None
        window   = None
        tab      = None


    def on_tab_switch_update(self, notebook, content = None, index = None):
        self.selected_files.clear()
        wid, tid = content.get_children()[0].get_name().split("|")

        self.fm_controller.set_wid_and_tid(wid, tid)
        self.set_path_text(wid, tid)
        self.set_window_title()

        wid, tid = None, None

    def get_id_from_tab_box(self, tab_box):
        return tab_box.tab.get_id()

    def get_tab_label(self, notebook, icon_grid):
        return notebook.get_tab_label(icon_grid.get_parent()).get_children()[0]

    def get_tab_close(self, notebook, icon_grid):
        return notebook.get_tab_label(icon_grid.get_parent()).get_children()[1]

    def get_tab_icon_grid_from_notebook(self, notebook):
        return notebook.get_children()[1].get_children()[0]

    def refresh_tab(data = None):
        state = self.get_current_state()
        state.tab.load_directory()
        self.load_store(state.tab, state.store)

        state = None

    def update_tab(self, tab_label, tab, store, wid, tid):
        self.load_store(tab, store)
        self.set_path_text(wid, tid)

        char_width = len(tab.get_end_of_path())
        tab_label.set_width_chars(char_width)
        tab_label.set_label(tab.get_end_of_path())
        self.set_window_title()
        self.set_file_watcher(tab)
        if not settings_manager.is_trace_debug():
            self.fm_controller.save_state()

    def do_action_from_bar_controls(self, widget, eve = None):
        action    = widget.get_name()
        wid, tid  = self.fm_controller.get_active_wid_and_tid()
        notebook  = self.builder.get_object(f"window_{wid}")
        store, tab_label = self.get_store_and_label_from_notebook(notebook, f"{wid}|{tid}")
        tab       = self.get_fm_window(wid).get_tab_by_id(tid)

        if action == "create_tab":
            dir = tab.get_current_directory()
            self.create_tab(wid, None, dir)
            if not settings_manager.is_trace_debug():
                self.fm_controller.save_state()

            return
        if action == "go_up":
            tab.pop_from_path()
        if action == "go_home":
            tab.set_to_home()
        if action == "refresh_tab":
            tab.load_directory()
        if action == "path_entry":
            focused_obj = self.window.get_focus()
            dir         = f"{tab.get_current_directory()}/"
            path        = widget.get_text()

            if isinstance(focused_obj, Gtk.Entry):
                self.process_path_menu(widget, tab, dir)

            action = None
            store  = None

            if path.endswith(".") or path == dir:
                tab_label = None
                notebook  = None
                wid, tid  = None, None
                path = None
                tab  = None
                return

            if not tab.set_path(path):
                tab_label = None
                notebook  = None
                wid, tid  = None, None
                path = None
                tab  = None
                return

        icon_grid = self.get_icon_grid_from_notebook(notebook, f"{wid}|{tid}")
        icon_grid.clear_and_set_new_store()
        self.update_tab(tab_label, tab, icon_grid.get_store(), wid, tid)

        action    = None
        wid, tid  = None, None
        notebook  = None
        store, tab_label = None, None
        path      = None
        tab       = None
        icon_grid = None


    def process_path_menu(self, gtk_entry, tab, dir):
        path_menu_buttons  = self.builder.get_object("path_menu_buttons")
        query              = gtk_entry.get_text().replace(dir, "")
        files              = tab.get_files() + tab.get_hidden()

        self.clear_children(path_menu_buttons)
        show_path_menu = False
        for file, hash, size in files:
            if os.path.isdir(f"{dir}{file}"):
                if query.lower() in file.lower():
                    button = Gtk.Button(label=file)
                    button.show()
                    button.connect("clicked", self.set_path_entry)
                    path_menu_buttons.add(button)
                    show_path_menu = True

        query = None
        files = None

        if not show_path_menu:
            path_menu_buttons = None
            event_system.emit("hide_path_menu")
        else:
            event_system.emit("show_path_menu")
            buttons = path_menu_buttons.get_children()
            path_menu_buttons = None

            if len(buttons) == 1:
                self.slowed_focus(buttons[0])

    @daemon_threaded
    def slowed_focus(self, button):
        time.sleep(0.05)
        GLib.idle_add(self.do_focused_click, *(button,))

    def do_focused_click(self, button):
        button.grab_focus()
        button.clicked()
        return False

    def set_path_entry(self, button = None, eve = None):
        self.path_auto_filled = True
        state      = self.get_current_state()
        path       = f"{state.tab.get_current_directory()}/{button.get_label()}"
        path_entry = self.builder.get_object("path_entry")

        path_entry.set_text(path)
        path_entry.grab_focus_without_selecting()
        path_entry.set_position(-1)
        event_system.emit("hide_path_menu")

        state      = None
        path       = None
        path_entry = None


    def show_hide_hidden_files(self):
        wid, tid = self.fm_controller.get_active_wid_and_tid()
        tab      = self.get_fm_window(wid).get_tab_by_id(tid)
        tab.set_hiding_hidden(not tab.is_hiding_hidden())
        tab.load_directory()
        self.builder.get_object("refresh_tab").released()

        wid, tid = None, None
        tab      = None