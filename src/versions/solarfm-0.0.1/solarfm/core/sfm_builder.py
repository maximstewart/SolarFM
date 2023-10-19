# Python imports

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Application imports



class SFMBuilder(Gtk.Builder):
    """docstring for SFMBuilder."""

    def __init__(self):
        super(SFMBuilder, self).__init__()

        self.objects = {}

    def get_object(self, id: str, use_gtk: bool = True) -> any:
        if not use_gtk:
            return self.objects[id]

        return super(SFMBuilder, self).get_object(id)

    def expose_object(self, id: str, object: any, use_gtk: bool = True) -> None:
        if not use_gtk:
            self.objects[id] = object
        else:
            super(SFMBuilder, self).expose_object(id, object)

    def dereference_object(self, id: str) -> None:
        del self.objects[id]
