# Python imports
import os

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk

# Application imports
from . import WidgetMixin




class TabMixin(WidgetMixin):
    """docstring for TabMixin"""

    def create_tab_from_ipc(data):
        self, path = data
        wid, tid   = self.window_controller.get_active_data()
        notebook   = self.builder.get_object(f"window_{wid}")
        if notebook.is_visible():
            self.create_tab(wid, path)
            return

        if not self.is_pane4_hidden:
            self.create_tab(4, path)
        elif not self.is_pane3_hidden:
            self.create_tab(3, path)
        elif not self.is_pane2_hidden:
            self.create_tab(2, path)
        elif not self.is_pane1_hidden:
            self.create_tab(1, path)


    def create_tab(self, wid, path=None):
        notebook    = self.builder.get_object(f"window_{wid}")
        path_entry  = self.builder.get_object(f"path_entry")
        view        = self.window_controller.add_view_for_window_by_nickname(f"window_{wid}")
        view.logger = self.logger

        view.set_wid(wid)
        if path: view.set_path(path)

        tab           = self.create_tab_widget(view)
        scroll, store = self.create_grid_iconview_widget(view, wid)
        # scroll, store = self.create_grid_treeview_widget(view, wid)
        index         = notebook.append_page(scroll, tab)

        self.window_controller.set_active_data(wid, view.get_tab_id())
        path_entry.set_text(view.get_current_directory())
        notebook.show_all()
        notebook.set_current_page(index)

        ctx = notebook.get_style_context()
        ctx.add_class("notebook-unselected-focus")
        notebook.set_tab_reorderable(scroll, True)
        self.load_store(view, store)
        self.set_window_title()
        self.set_file_watcher(view)




    def close_tab(self, button, eve=None):
        notebook = button.get_parent().get_parent()
        tid      = self.get_tab_id_from_tab_box(button.get_parent())
        wid      = int(notebook.get_name()[-1])
        scroll   = self.builder.get_object(f"{wid}|{tid}")
        page     = notebook.page_num(scroll)
        view     = self.get_fm_window(wid).get_view_by_id(tid)
        watcher  = view.get_dir_watcher()

        watcher.cancel()
        self.get_fm_window(wid).delete_view_by_id(tid)
        notebook.remove_page(page)
        self.window_controller.save_state()
        self.set_window_title()

    def on_tab_reorder(self, child, page_num, new_index):
        wid, tid = page_num.get_name().split("|")
        window   = self.get_fm_window(wid)
        view     = None

        for i, view in enumerate(window.views):
            if view.id == tid:
                _view   = window.get_view_by_id(tid)
                watcher = _view.get_dir_watcher()
                watcher.cancel()
                window.views.insert(new_index, window.views.pop(i))

        view = window.get_view_by_id(tid)
        self.set_file_watcher(view)
        self.window_controller.save_state()

    def on_tab_switch_update(self, notebook, content=None, index=None):
        self.selected_files.clear()
        wid, tid = content.get_children()[0].get_name().split("|")
        self.window_controller.set_active_data(wid, tid)
        self.set_path_text(wid, tid)
        self.set_window_title()

    def get_tab_id_from_tab_box(self, tab_box):
        tid = tab_box.get_children()[2]
        return tid.get_text()

    def get_tab_label(self, notebook, iconview):
        return notebook.get_tab_label(iconview.get_parent()).get_children()[0]

    def get_tab_close(self, notebook, iconview):
        return notebook.get_tab_label(iconview.get_parent()).get_children()[1]

    def get_tab_iconview_from_notebook(self, notebook):
        return notebook.get_children()[1].get_children()[0]

    def refresh_tab(data=None):
        wid, tid, view, iconview, store = self.get_current_state()
        view.load_directory()
        self.load_store(view, store)

    def update_view(self, tab_label, view, store, wid, tid):
        self.load_store(view, store)
        self.set_path_text(wid, tid)

        char_width = len(view.get_end_of_path())
        tab_label.set_width_chars(char_width)
        tab_label.set_label(view.get_end_of_path())
        self.set_window_title()
        self.set_file_watcher(view)
        self.window_controller.save_state()

    def do_action_from_bar_controls(self, widget, eve=None):
        action    = widget.get_name()
        wid, tid  = self.window_controller.get_active_data()
        notebook  = self.builder.get_object(f"window_{wid}")
        store, tab_label = self.get_store_and_label_from_notebook(notebook, f"{wid}|{tid}")
        view      = self.get_fm_window(wid).get_view_by_id(tid)

        if action == "go_up":
            view.pop_from_path()
        if action == "go_home":
            view.set_to_home()
        if action == "refresh_view":
            view.load_directory()
        if action == "create_tab":
            dir = view.get_current_directory()
            self.create_tab(wid, dir)
            self.window_controller.save_state()
            return
        if action == "path_entry":
            focused_obj = self.window.get_focus()
            dir         = f"{view.get_current_directory()}/"
            path        = widget.get_text()

            if isinstance(focused_obj, Gtk.Entry):
                button_box  = self.path_menu.get_children()[0].get_children()[0].get_children()[0]
                query       = widget.get_text().replace(dir, "")
                files       = view.files + view.hidden

                self.clear_children(button_box)
                show_path_menu = False
                for file in files:
                    if os.path.isdir(f"{dir}{file}"):
                        if query.lower() in file.lower():
                            button = Gtk.Button(label=file)
                            button.show()
                            button.connect("clicked", self.set_path_entry)
                            button_box.add(button)
                            show_path_menu = True

                if not show_path_menu:
                    self.path_menu.popdown()
                else:
                    self.path_menu.popup()
                    widget.grab_focus_without_selecting()
                    widget.set_position(-1)

            if path.endswith(".") or path == dir:
                return

            traversed = view.set_path(path)
            if not traversed:
                return

        self.update_view(tab_label, view, store, wid, tid)

        try:
            widget.grab_focus_without_selecting()
            widget.set_position(-1)
        except Exception as e:
            pass

    def set_path_entry(self, button=None, eve=None):
        wid, tid, view, iconview, store = self.get_current_state()
        path       = f"{view.get_current_directory()}/{button.get_label()}"
        path_entry = self.builder.get_object("path_entry")
        path_entry.set_text(path)
        path_entry.grab_focus_without_selecting()
        path_entry.set_position(-1)
        self.path_menu.popdown()

    def keyboard_close_tab(self):
        wid, tid  = self.window_controller.get_active_data()
        notebook  = self.builder.get_object(f"window_{wid}")
        scroll    = self.builder.get_object(f"{wid}|{tid}")
        page      = notebook.page_num(scroll)
        view      = self.get_fm_window(wid).get_view_by_id(tid)
        watcher   = view.get_dir_watcher()
        watcher.cancel()

        self.get_fm_window(wid).delete_view_by_id(tid)
        notebook.remove_page(page)
        self.window_controller.save_state()
        self.set_window_title()

    # File control events
    def show_hide_hidden_files(self):
        wid, tid = self.window_controller.get_active_data()
        view     = self.get_fm_window(wid).get_view_by_id(tid)
        view.hide_hidden = not view.hide_hidden
        view.load_directory()
        self.builder.get_object("refresh_view").released()