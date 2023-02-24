# Python imports

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gio

# Application imports




class IOWidget(Gtk.Box):
    """docstring for IOWidget"""

    def __init__(self, action, file):
        super(IOWidget, self).__init__()
        self._action    = action
        self._file      = file
        self._basename  = self._file.get_basename()

        self.cancle_eve = Gio.Cancellable.new()
        self.progress   = None

        self._setup_styling()
        self._setup_signals()
        self._load_widgets()

        self.show_all()


    def _setup_styling(self):
        self.set_orientation(1)

    def _setup_signals(self):
        ...

    def _load_widgets(self):
        stats         = Gtk.Box()
        label         = Gtk.Label()
        cncl_button   = Gtk.Button(label="Cancel")
        del_button    = Gtk.Button(label="Clear")
        self.progress = Gtk.ProgressBar()

        label.set_label(self._basename)
        self.progress.set_show_text(True)
        self.progress.set_text(f"{self._action.upper()}ING")
        stats.set_orientation(0)

        stats.pack_end(del_button, False, False, 5)
        del_button.connect("clicked", self.delete_self, ())

        if not self._action in ("create", "rename"):
            stats.pack_end(cncl_button, False, False, 5)
            cncl_button.connect("clicked", self.do_cancel, *(self, self.cancle_eve))

        stats.add(self.progress)
        self.add(label)
        self.add(stats)

    def do_cancel(self, widget, container, eve):
        logger.info(f"Canceling: [{self._action}] of {self._basename} ...")
        eve.cancel()

    def update_progress(self, current, total, eve=None):
        self.progress.set_fraction(current/total)

    def finish_callback(self, file, task=None, eve=None):
        if self._action == "move" or self._action == "rename":
            status = self._file.move_finish(task)
        if self._action == "copy":
            status = self._file.copy_finish(task)

        if status:
            self.delete_self()
        else:
            logger.info(f"{self._action} of {self._basename} failed...")

    def delete_self(self, widget=None, eve=None):
        self.get_parent().remove(self)
