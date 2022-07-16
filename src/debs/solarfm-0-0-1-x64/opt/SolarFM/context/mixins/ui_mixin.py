# Python imports

# Gtk imports

# Application imports
from .show_hide_mixin import ShowHideMixin
from .ui.widget_file_action_mixin import WidgetFileActionMixin
from .ui.pane_mixin import PaneMixin
from .ui.window_mixin import WindowMixin
from .show_hide_mixin import ShowHideMixin


class UIMixin(WidgetFileActionMixin, PaneMixin, WindowMixin, ShowHideMixin):
    pass
