# Python imports

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf
from gi.repository import Gio

# Application imports
from .signals.icon_view_signals_mixin import IconViewSignalsMixin




class IconView(IconViewSignalsMixin, Gtk.FlowBox):
    """docstring for IconView."""

    def __init__(self, _tab_state):
        super(IconView, self).__init__()
        self.tab_state      = _tab_state
        self.selected_files = []
        self.icon_theme     = settings.get_icon_theme()

        self._setup_styling()
        self._setup_signals()
        # self._setup_dnd()
        self.load_store()

        self.show_all()


    def _emmit_signal_to_file_view(self, signal_type):
        self.get_parent().get_parent().emit(signal_type, None)

    def _setup_styling(self):
        self.set_selection_mode(Gtk.SelectionMode.MULTIPLE)
        self.set_valign(Gtk.Align.START)
        self.set_column_spacing(15)
        self.set_row_spacing(15)
        self.set_homogeneous(True)

    def _setup_signals(self):
        self.set_activate_on_single_click(False)
        self.connect("child-activated", self.icon_double_click)

        # self.connect("drag-data-get",        self.on_drag_set)
        # self.connect("drag-data-received",   self.on_drag_data_received)
        # self.connect("drag-motion",          self.on_drag_motion)


    # NOTE: This gets called by a txt box which then shows/hides the flowbox child
    #       https://stackoverflow.com/questions/55828169/how-to-filter-gtk-flowbox-children-with-gtk-entrysearch
    def search_filter(self, text):
        def filter_func(fb_child, text):
            if text.lower() in fb_child.get_name().lower():
                return True
            else:
                return False

        self.set_filter_func(filter_func, text)


    def _setup_dnd(self):
        URI_TARGET_TYPE  = 80
        uri_target       = Gtk.TargetEntry.new('text/uri-list', Gtk.TargetFlags(0), URI_TARGET_TYPE)
        targets          = [ uri_target ]
        action           = Gdk.DragAction.COPY
        self.enable_model_drag_dest(targets, action)
        self.enable_model_drag_source(0, targets, action)

    def _clear_children(self, widget: type) -> None:
        ''' Clear children of a gtk widget. '''
        for child in widget.get_children():
            widget.remove(child)














# class IconView(IconViewSignalsMixin, Gtk.IconView):
#     """docstring for IconView."""
#
#     def __init__(self, _tab_state):
#         super(IconView, self).__init__()
#         self.store          = None
#         self.tab_state      = _tab_state
#         self.selected_files = []
#         self.icon_theme     = Gtk.IconTheme.get_default()
#
#         self._setup_store()
#         self._setup_styling()
#         self._setup_signals()
#         self._setup_dnd()
#         self.load_store()
#
#         self.show_all()
#
#
#     def _setup_store(self):
#         self.store = Gtk.ListStore(GdkPixbuf.Pixbuf or GdkPixbuf.PixbufAnimation or None, str or None)
#         self.set_model(self.store)
#         self.set_pixbuf_column(0)
#         self.set_text_column(1)
#
#     def _setup_styling(self):
#         self.set_item_orientation(1)
#         self.set_selection_mode(3)
#         self.set_item_width(96)
#         self.set_item_padding(8)
#         self.set_margin(12)
#         self.set_row_spacing(18)
#         self.set_columns(-1)
#         self.set_spacing(12)
#         self.set_column_spacing(18)
#
#     def _setup_signals(self):
#         # self.connect("button_release_event", self.icon_single_click)
#         self.connect("item-activated",       self.icon_double_click)
#         self.connect("selection-changed",    self.set_selected_items)
#         # self.connect("drag-data-get",        self.on_drag_set)
#         # self.connect("drag-data-received",   self.on_drag_data_received)
#         # self.connect("drag-motion",          self.on_drag_motion)
#         pass
#
#     def _setup_dnd(self):
#         URI_TARGET_TYPE  = 80
#         uri_target       = Gtk.TargetEntry.new('text/uri-list', Gtk.TargetFlags(0), URI_TARGET_TYPE)
#         targets          = [ uri_target ]
#         action           = Gdk.DragAction.COPY
#         self.enable_model_drag_dest(targets, action)
#         self.enable_model_drag_source(0, targets, action)
#
#     def set_selected_items(self, icons_grid):
#         self.selected_files = self.get_selected_items()
