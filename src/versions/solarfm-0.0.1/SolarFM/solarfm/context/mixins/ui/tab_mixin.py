# Python imports
import os

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Application imports
from .widget_mixin import WidgetMixin




class TabMixin(WidgetMixin):
    """docstring for TabMixin"""

    def create_tab(self, wid, path=None):
        notebook    = self.builder.get_object(f"window_{wid}")
        path_entry  = self.builder.get_object(f"path_entry")
        tab         = self.fm_controller.add_tab_for_window_by_nickname(f"window_{wid}")
        tab.logger  = self.logger

        tab.set_wid(wid)
        if path: tab.set_path(path)

        tab_widget    = self.create_tab_widget(tab)
        scroll, store = self.create_icon_grid_widget(tab, wid)
        # TODO: Fix global logic to make the below work too
        # scroll, store = self.create_icon_tree_widget(tab, wid)
        index         = notebook.append_page(scroll, tab_widget)

        self.fm_controller.set__wid_and_tid(wid, tab.get_id())
        path_entry.set_text(tab.get_current_directory())
        notebook.show_all()
        notebook.set_current_page(index)

        ctx = notebook.get_style_context()
        ctx.add_class("notebook-unselected-focus")
        notebook.set_tab_reorderable(scroll, True)
        self.load_store(tab, store)
        self.set_window_title()
        self.set_file_watcher(tab)




    def close_tab(self, button, eve=None):
        notebook = button.get_parent().get_parent()
        wid      = int(notebook.get_name()[-1])
        tid      = self.get_id_from_tab_box(button.get_parent())
        scroll   = self.builder.get_object(f"{wid}|{tid}")
        page     = notebook.page_num(scroll)
        tab      = self.get_fm_window(wid).get_tab_by_id(tid)
        watcher  = tab.get_dir_watcher()

        watcher.cancel()
        self.get_fm_window(wid).delete_tab_by_id(tid)
        notebook.remove_page(page)
        self.fm_controller.save_state()
        self.set_window_title()

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
        self.fm_controller.save_state()

    def on_tab_switch_update(self, notebook, content=None, index=None):
        self.selected_files.clear()
        wid, tid = content.get_children()[0].get_name().split("|")
        self.fm_controller.set__wid_and_tid(wid, tid)
        self.set_path_text(wid, tid)
        self.set_window_title()

    def get_id_from_tab_box(self, tab_box):
        return tab_box.get_children()[2].get_text()

    def get_tab_label(self, notebook, icon_grid):
        return notebook.get_tab_label(icon_grid.get_parent()).get_children()[0]

    def get_tab_close(self, notebook, icon_grid):
        return notebook.get_tab_label(icon_grid.get_parent()).get_children()[1]

    def get_tab_icon_grid_from_notebook(self, notebook):
        return notebook.get_children()[1].get_children()[0]

    def refresh_tab(data=None):
        state = self.get_current_state()
        state.tab.load_directory()
        self.load_store(state.tab, state.store)

    def update_tab(self, tab_label, tab, store, wid, tid):
        self.load_store(tab, store)
        self.set_path_text(wid, tid)

        char_width = len(tab.get_end_of_path())
        tab_label.set_width_chars(char_width)
        tab_label.set_label(tab.get_end_of_path())
        self.set_window_title()
        self.set_file_watcher(tab)
        self.fm_controller.save_state()

    def do_action_from_bar_controls(self, widget, eve=None):
        action    = widget.get_name()
        wid, tid  = self.fm_controller.get_active_wid_and_tid()
        notebook  = self.builder.get_object(f"window_{wid}")
        store, tab_label = self.get_store_and_label_from_notebook(notebook, f"{wid}|{tid}")
        tab       = self.get_fm_window(wid).get_tab_by_id(tid)

        if action == "create_tab":
            dir = tab.get_current_directory()
            self.create_tab(wid, dir)
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
                path_menu_buttons  = self.builder.get_object("path_menu_buttons")
                query              = widget.get_text().replace(dir, "")
                files              = tab.get_files() + tab.get_hidden()

                self.clear_children(path_menu_buttons)
                show_path_menu = False
                for file, hash in files:
                    if os.path.isdir(f"{dir}{file}"):
                        if query.lower() in file.lower():
                            button = Gtk.Button(label=file)
                            button.show()
                            button.connect("clicked", self.set_path_entry)
                            path_menu_buttons.add(button)
                            show_path_menu = True

                if not show_path_menu:
                    self.path_menu.popdown()
                else:
                    self.path_menu.popup()
                    widget.grab_focus_without_selecting()
                    widget.set_position(-1)

            if path.endswith(".") or path == dir:
                return

            if not tab.set_path(path):
                return

        self.update_tab(tab_label, tab, store, wid, tid)

        try:
            widget.grab_focus_without_selecting()
            widget.set_position(-1)
        except Exception as e:
            pass

    def set_path_entry(self, button=None, eve=None):
        state      = self.get_current_state()
        path       = f"{state.tab.get_current_directory()}/{button.get_label()}"
        path_entry = self.builder.get_object("path_entry")
        path_entry.set_text(path)
        path_entry.grab_focus_without_selecting()
        path_entry.set_position(-1)
        self.path_menu.popdown()

    def show_hide_hidden_files(self):
        wid, tid = self.fm_controller.get_active_wid_and_tid()
        tab      = self.get_fm_window(wid).get_tab_by_id(tid)
        tab.set_hiding_hidden(not tab.is_hiding_hidden())
        tab.load_directory()
        self.builder.get_object("refresh_tab").released()
