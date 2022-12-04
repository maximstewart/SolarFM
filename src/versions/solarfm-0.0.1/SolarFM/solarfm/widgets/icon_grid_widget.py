# Python imports

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf


# Application imports




class IconGridWidget(Gtk.IconView):
    """docstring for IconGridWidget"""

    def __init__(self):
        super(IconGridWidget, self).__init__()

        self._store = None

        self._setup_styling()
        self._setup_signals()
        self._set_up_dnd()
        self._load_widgets()

        self.show_all()

    def get_store(self):
        return self._store

    def _setup_styling(self):
        self.set_pixbuf_column(0)
        self.set_text_column(1)

        self.set_item_orientation(1)
        self.set_selection_mode(3)
        self.set_item_width(96)
        self.set_item_padding(8)
        self.set_margin(12)
        self.set_row_spacing(18)
        self.set_columns(-1)
        self.set_spacing(12)
        self.set_column_spacing(18)

    def _setup_signals(self):
        ...

    def _setup_additional_signals(self, grid_icon_single_click,
                                        grid_icon_double_click,
                                        grid_set_selected_items,
                                        grid_on_drag_set,
                                        grid_on_drag_data_received,
                                        grid_on_drag_motion):

        self.connect("button_release_event", grid_icon_single_click)
        self.connect("item-activated",       grid_icon_double_click)
        self.connect("selection-changed",    grid_set_selected_items)
        self.connect("drag-data-get",        grid_on_drag_set)
        self.connect("drag-data-received",   grid_on_drag_data_received)
        self.connect("drag-motion",          grid_on_drag_motion)

    def _load_widgets(self):
        self._store = Gtk.ListStore(GdkPixbuf.Pixbuf or GdkPixbuf.PixbufAnimation or None, str or None)
        self.set_model(self._store)

    def _set_up_dnd(self):
        URI_TARGET_TYPE  = 80
        uri_target       = Gtk.TargetEntry.new('text/uri-list', Gtk.TargetFlags(0), URI_TARGET_TYPE)
        targets          = [ uri_target ]
        action           = Gdk.DragAction.COPY
        self.enable_model_drag_dest(targets, action)
        self.enable_model_drag_source(0, targets, action)
