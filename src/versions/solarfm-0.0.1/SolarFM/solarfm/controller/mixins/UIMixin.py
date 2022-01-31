# Python imports

# Gtk imports

# Application imports
from . import ShowHideMixin
from .ui import *


class UIMixin(WidgetFileActionMixin, PaneMixin, WindowMixin, ShowHideMixin):
    pass
