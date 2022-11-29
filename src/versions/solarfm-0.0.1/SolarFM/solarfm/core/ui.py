# Python imports

# Gtk imports

# Application imports
from .mixins.show_hide_mixin import ShowHideMixin
from .mixins.ui.pane_mixin import PaneMixin
from .mixins.ui.window_mixin import WindowMixin


class UI(PaneMixin, WindowMixin, ShowHideMixin):
    ...
