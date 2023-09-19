# Python imports
from dataclasses import dataclass, field
from dataclasses import asdict

# Gtk imports

# Application imports
from .config import Config
from .filters import Filters
from .theming import Theming
from .debugging import Debugging


@dataclass
class Settings:
    load_defaults: bool  = True
    config: Config       = field(default_factory=lambda: Config())
    filters: Filters     = field(default_factory=lambda: Filters())
    theming: Theming     = field(default_factory=lambda: Theming())
    debugging: Debugging = field(default_factory=lambda: Debugging())

    def __post_init__(self):
        if not self.load_defaults:
            self.load_defaults = False
            self.config        = Config(**self.config)
            self.filters       = Filters(**self.filters)
            self.theming       = Theming(**self.theming)
            self.debugging     = Debugging(**self.debugging)

    def as_dict(self):
        return asdict(self)
