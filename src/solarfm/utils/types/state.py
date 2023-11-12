# Python imports
from dataclasses import dataclass

# Lib imports
from gi.overrides.Gtk import IconView
from gi.overrides.Gtk import ListStore

# Application imports



@dataclass(slots=True)
class State:
    fm_controller: any = None
    notebooks: any = None
    wid: int = None
    tid: int = None
    tab: type = None
    icon_grid: IconView = None
    store: ListStore = None
    uris:           list   = None
    uris_raw:       list   = None
    selected_files: list   = None
    to_copy_files:  list   = None
    to_cut_files:   list   = None
    message_dialog: type    = None
    user_pass_dialog: type  = None
