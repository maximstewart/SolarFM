# Python imports

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Application imports
from .file_view import FileView




class FilesWidget(Gtk.Notebook):
    """docstring for FilesWidget."""

    ccount = 0

    def __new__(cls, *args, **kwargs):
        obj        = super(FilesWidget, cls).__new__(cls)
        cls.ccount += 1

        return obj

    def __init__(self):
        super(FilesWidget, self).__init__()

        self.set_group_name("file_window")

        self.NAME = f"window_{self.ccount}"
        builder   = settings.get_builder()
        builder.expose_object(self.NAME, self)

        self._add_action_widgets()
        self._setup_styling()
        self._setup_signals()

        self.show_all()


    def _setup_styling(self):
        self.set_scrollable(True)
        self.set_show_tabs(True)
        self.set_show_border(False)
        self.set_hexpand(True)

        self.set_margin_top(5)
        self.set_margin_bottom(5)
        self.set_margin_start(5)
        self.set_margin_end(5)

    def _setup_signals(self):
        # self.connect("close-view", self.close_view)
        event_system.subscribe("load-window-state", self.load_window_state)

    def _add_action_widgets(self):
        start_box = Gtk.Box()
        end_box   = Gtk.Box()

        search = Gtk.SearchEntry()
        search.set_placeholder_text("Search...")
        search.connect("changed", self._do_query)

        home_btn = Gtk.Button()
        home_btn.set_image( Gtk.Image.new_from_icon_name("gtk-home", 4) )
        home_btn.set_always_show_image(True)
        home_btn.connect("released", self.do_action, ("go_home_dir"))

        up_btn = Gtk.Button()
        up_btn.set_image( Gtk.Image.new_from_icon_name("up", 4) )
        up_btn.set_always_show_image(True)
        up_btn.connect("released", self.do_action, ("go_up_dir"))

        refresh_btn = Gtk.Button()
        refresh_btn.set_image( Gtk.Image.new_from_icon_name("gtk-refresh", 4) )
        refresh_btn.set_always_show_image(True)
        refresh_btn.connect("released", self.do_action, ("refresh_dir"))

        add_btn = Gtk.Button()
        add_btn.set_image( Gtk.Image.new_from_icon_name("add", 4) )
        add_btn.set_always_show_image(True)
        add_btn.connect("released", self.create_view)

        start_box.add(home_btn)
        start_box.add(add_btn)
        end_box.add(search)
        end_box.add(up_btn)
        end_box.add(refresh_btn)

        start_box.show_all()
        end_box.show_all()

        # PACKTYPE: 0 Start, 1 = End
        self.set_action_widget(start_box, 0)
        self.set_action_widget(end_box, 1)

    def _do_query(self, widget):
        text = widget.get_text()
        page = self.get_nth_page( self.get_current_page() )
        page.icon_view.search_filter(text)


    def load_window_state(self, win_name=None, tabs=None):
        if win_name == self.NAME:
            if len(tabs) > 0:
                for tab in tabs:
                    self.create_view()
                    self.load_tab(tab)
            else:
                self.create_view()

    def create_view(self, widget = None):
        file_view = FileView()
        index = self.append_page(file_view, file_view.tab_widget)
        self.set_current_page(index)

        return file_view

    def load_tab(self, path = None):
        if path:
            file_view = self.get_nth_page( self.get_current_page() )
            file_view.set_path(path)


    def do_action(self, widget = None, action = None):
        file_view = self.get_nth_page( self.get_current_page() )

        if action == "refresh_dir":
            file_view.icon_view.refresh_dir()

        if action == "go_up_dir":
            file_view.icon_view.go_up_dir()

        if action == "go_home_dir":
            file_view.icon_view.go_home_dir()


    def close_view(self, parent, data = None):
        widget = data[0]
        page   = self.page_num(widget)

        # watcher  = widget.tab_state.get_dir_watcher()
        # watcher.cancel()
        if self.get_n_pages() > 1:
            self.remove_page(page)

        # NOTE: Will prob try and call a window custom signal...
        # self.fm_controller.save_state()
        # self.set_window_title()
