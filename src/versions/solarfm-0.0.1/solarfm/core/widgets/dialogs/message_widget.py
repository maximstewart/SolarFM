# Python imports

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Application imports




class MessageWidget(Gtk.MessageDialog):
    """docstring for MessageWidget."""

    def __init__(self):
        super(MessageWidget, self).__init__()

        self._setup_styling()
        self._setup_signals()
        self._load_widgets()


    def _setup_styling(self):
        self.type = Gtk.MessageType.WARNING

    def _setup_signals(self):
        ...

    def _load_widgets(self):
        message_area = self.get_message_area()
        message_area.get_children()[0].set_label("Alert!")
        message_area.show_all()

        self.set_image( Gtk.Image.new_from_icon_name("user-alert", 16) )
        self.add_buttons(Gtk.STOCK_NO, Gtk.ResponseType.NO)
        self.add_buttons(Gtk.STOCK_YES, Gtk.ResponseType.YES)
