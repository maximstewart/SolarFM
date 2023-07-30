# Python imports
from dataclasses import dataclass

# Gtk imports

# Application imports
from .config import Config
from .filters import Filters
from .theming import Theming
from .debugging import Debugging


@dataclass
class Settings:
    config: Config
    filters: Filters
    theming: Theming
    debugging: Debugging

    def __post_init__(self):
        self.config    = Config(**self.config)
        self.filters   = Filters(**self.filters)
        self.theming   = Theming(**self.theming)
        self.debugging = Debugging(**self.debugging)
