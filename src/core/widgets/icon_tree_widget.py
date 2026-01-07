# Python imports

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf

# Application imports




class IconTreeWidget(Gtk.TreeView):
    """docstring for IconTreeWidget"""

    def __init__(self):
        super(IconTreeWidget, self).__init__()

        self._store = None

        self._setup_styling()
        self._setup_signals()
        self._set_up_dnd()
        self._load_widgets()

        self.show_all()

    def get_store(self):
        return self._store

    def _setup_styling(self):
        self.set_search_column(1)
        self.set_rubber_banding(True)
        self.set_headers_visible(False)
        self.set_enable_tree_lines(False)

    def _setup_signals(self):
        ...

    def _setup_additional_signals(self, grid_icon_single_click,
                                        grid_icon_double_click,
                                        grid_on_drag_set,
                                        grid_on_drag_data_received,
                                        grid_on_drag_motion):

        self.connect("button_release_event", self.grid_icon_single_click)
        self.connect("row-activated",        self.grid_icon_double_click)
        self.connect("drag-data-get",        self.grid_on_drag_set)
        self.connect("drag-data-received",   self.grid_on_drag_data_received)
        self.connect("drag-motion",          self.grid_on_drag_motion)

    def _load_widgets(self):
        self._store = Gtk.TreeStore(GdkPixbuf.Pixbuf or GdkPixbuf.PixbufAnimation or None, str or None)
        column = Gtk.TreeViewColumn("Icons")
        icon   = Gtk.CellRendererPixbuf()
        name   = Gtk.CellRendererText()
        selec  = self.get_selection()

        self.set_model(self._store)
        selec.set_mode(3)

        column.pack_start(icon, False)
        column.pack_start(name, True)
        column.add_attribute(icon, "pixbuf", 0)
        column.add_attribute(name, "text", 1)
        column.set_expand(False)
        column.set_sizing(2)
        column.set_min_width(120)
        column.set_max_width(74)

        self.append_column(column)


    def _set_up_dnd(self):
        URI_TARGET_TYPE  = 80
        uri_target       = Gtk.TargetEntry.new('text/uri-list', Gtk.TargetFlags(0), URI_TARGET_TYPE)
        targets          = [ uri_target ]
        action           = Gdk.DragAction.COPY
        self.enable_model_drag_dest(targets, action)
        self.enable_model_drag_source(0, targets, action)
