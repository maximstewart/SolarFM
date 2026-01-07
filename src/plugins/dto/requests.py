# Python imports
from dataclasses import dataclass, field

# Lib imports

# Application imports


@dataclass
class Requests:
    ui_target: str        = ""
    ui_target_id: str     = ""
    pass_events: bool     = False
    pass_fm_events: bool  = False
    pass_ui_objects: list = field(default_factory = lambda: [])
    bind_keys: list       = field(default_factory = lambda: [])
