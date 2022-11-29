# Python imports

# Gtk imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Application imports


class FilePreviewWidget(Gtk.LinkButton):
    def __init__(self, path, file):
        super(FilePreviewWidget, self).__init__()
        self.set_label(file)
        self.set_uri(f"file://{path}")
        self.show_all()
