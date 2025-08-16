# Python imports
import gc

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

        self._handler_ids = []

        self._setup_styling()
        self._setup_signals()
        self._set_up_dnd()
        self._load_widgets()

        self.show_all()


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

        self._handler_ids.append(self.connect("button_release_event", grid_icon_single_click))
        self._handler_ids.append(self.connect("item-activated",       grid_icon_double_click))
        self._handler_ids.append(self.connect("selection-changed",    grid_set_selected_items))
        self._handler_ids.append(self.connect("drag-data-get",        grid_on_drag_set))
        self._handler_ids.append(self.connect("drag-data-received",   grid_on_drag_data_received))
        self._handler_ids.append(self.connect("drag-motion",          grid_on_drag_motion))

    def _load_widgets(self):
        self.clear_and_set_new_store()

    def _set_up_dnd(self):
        URI_TARGET_TYPE  = 80
        uri_target       = Gtk.TargetEntry.new('text/uri-list', Gtk.TargetFlags(0), URI_TARGET_TYPE)
        targets          = [ uri_target ]
        action           = Gdk.DragAction.COPY
        self.enable_model_drag_dest(targets, action)
        self.enable_model_drag_source(0, targets, action)


    def get_store(self):
        return self.get_model()

    def clear_and_set_new_store(self):
        self._clear_store()
        self.set_model(
            Gtk.ListStore(
                GdkPixbuf.Pixbuf or GdkPixbuf.PixbufAnimation or None, str or None
            )
        )

    def clear_signals_and_data(self):
        self.unset_model_drag_dest()
        self.unset_model_drag_source()

        for handle_id in self._handler_ids:
            self.disconnect(handle_id)

        self._handler_ids.clear()
        self._clear_store()

    def _clear_store(self):
        store = self.get_model()
        self.set_model(None)

        if not store: return

        iter = store.get_iter_first()
        while iter:
            icon = store.get_value(iter, 0)

            store.set_value(iter, 0, None)
            store.set_value(iter, 1, None)

            iter = store.iter_next(iter)

            if icon:
                logger.debug(f"Reference count for icon is: {icon.__grefcount__}")
                icon.run_dispose()
                del icon

        store.clear()
        store.run_dispose()
        del store

        gc.collect()
