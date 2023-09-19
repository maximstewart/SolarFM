# Python imports

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk

# Application imports




class UserPassWidget(Gtk.Dialog):
    """docstring for UserPassWidget."""

    def __init__(self):
        super(UserPassWidget, self).__init__()

        self.user_input = Gtk.Entry()
        self.pass_input = Gtk.Entry()

        self._setup_styling()
        self._setup_signals()
        self._subscribe_to_events()
        self._load_widgets()


    def _setup_styling(self):
        self.set_modal(True)
        self.set_type_hint(Gdk.WindowTypeHint.DIALOG)

        self.user_input.set_placeholder_text("User:")
        self.pass_input.set_placeholder_text("Password:")
        self.pass_input.set_visibility(False)

    def _setup_signals(self):
        # self.connect("response", self.on_response)
        ...

    def _subscribe_to_events(self):
        ...

    def _load_widgets(self):
        vbox  = self.get_content_area()
        label = Gtk.Label(label="User & Password")
        vbox.add(label)
        vbox.add(self.user_input)
        vbox.add(self.pass_input)
        vbox.show_all()

        self.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                            "Skip Input", Gtk.ResponseType.CLOSE,
                            "Submit Input", Gtk.ResponseType.OK
                        )

    def do_response(self, response_id):
        self.hide()
        return response_id

    # def on_response(self, widget, response_id):
    #     self.hide()
    #     return response_id
