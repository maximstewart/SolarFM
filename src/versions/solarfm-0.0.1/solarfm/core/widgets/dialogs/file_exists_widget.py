# Python imports
import inspect

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GLib

# Application imports




class FileExistsWidget:
    """docstring for FileExistsWidget."""

    def __init__(self):
        super(FileExistsWidget, self).__init__()
        _GLADE_FILE   = f"{settings.get_ui_widgets_path()}/file_exists_ui.glade"
        builder       = settings.get_builder()
        self._builder = Gtk.Builder()

        self._builder.add_from_file(_GLADE_FILE)

        self.file_exists_dialog       = self._builder.get_object("file_exists_dialog")
        self._exists_file_label       = self._builder.get_object("exists_file_label")
        self._exists_file_diff_from   = self._builder.get_object("exists_file_diff_from")
        self._exists_file_diff_to     = self._builder.get_object("exists_file_diff_to")
        self._exists_file_field       = self._builder.get_object("exists_file_field")
        self._exists_file_from        = self._builder.get_object("exists_file_from")
        self._exists_file_to          = self._builder.get_object("exists_file_to")
        self._exists_file_rename_bttn = self._builder.get_object("exists_file_rename_bttn")

        builder.expose_object(f"file_exists_dialog", self.file_exists_dialog)
        builder.expose_object(f"exists_file_diff_from", self._exists_file_diff_from)
        builder.expose_object(f"exists_file_diff_to", self._exists_file_diff_to)
        builder.expose_object(f"exists_file_field", self._exists_file_field)
        builder.expose_object(f"exists_file_rename_bttn", self._exists_file_rename_bttn)

        self._setup_styling()
        self._setup_signals()
        self._load_widgets()


    def _setup_styling(self):
        ...

    def _setup_signals(self):
        event_system.subscribe("setup_exists_data", self.setup_exists_data)
        event_system.subscribe("show_exists_page", self.show_exists_page)


        classes  = [self]
        handlers = {}
        for c in classes:
            methods = None
            try:
                methods = inspect.getmembers(c, predicate=inspect.ismethod)
                handlers.update(methods)
            except Exception as e:
                logger.debug(repr(e))

        self._builder.connect_signals(handlers)

    def _load_widgets(self):
        ...

    def show_exists_page(self, widget=None, eve=None):
        response = self.file_exists_dialog.run()
        self.file_exists_dialog.hide()

        if response == Gtk.ResponseType.OK:
            return "rename"
        if response == Gtk.ResponseType.ACCEPT:
            return "rename_auto"
        if response == Gtk.ResponseType.CLOSE:
            return "rename_auto_all"
        if response == Gtk.ResponseType.YES:
            return "overwrite"
        if response == Gtk.ResponseType.APPLY:
            return "overwrite_all"
        if response == Gtk.ResponseType.NO:
            return "skip"
        if response == Gtk.ResponseType.REJECT:
            return "skip_all"

    def hide_exists_page_rename(self, widget=None, eve=None):
        self.file_exists_dialog.response(Gtk.ResponseType.OK)

    def hide_exists_page_auto_rename(self, widget=None, eve=None):
        self.file_exists_dialog.response(Gtk.ResponseType.ACCEPT)

    def hide_exists_page_auto_rename_all(self, widget=None, eve=None):
        self.file_exists_dialog.response(Gtk.ResponseType.CLOSE)

    def setup_exists_data(self, from_file, to_file):
        from_info             = from_file.query_info("standard::*,time::modified", 0, cancellable=None)
        to_info               = to_file.query_info("standard::*,time::modified", 0, cancellable=None)
        from_date             = from_info.get_modification_date_time()
        to_date               = to_info.get_modification_date_time()
        from_size             = from_info.get_size()
        to_size               = to_info.get_size()

        self._exists_file_from.set_label(from_file.get_parent().get_path())
        self._exists_file_to.set_label(to_file.get_parent().get_path())
        self._exists_file_label.set_label(to_file.get_basename())
        self._exists_file_field.set_text(to_file.get_basename())

        # Returns: -1, 0 or 1 if dt1 is less than, equal to or greater than dt2.
        age       = GLib.DateTime.compare(from_date, to_date)
        age_text  = "( same time )"
        if age == -1:
            age_text = "older"
        if age == 1:
            age_text = "newer"

        size_text = "( same size )"
        if from_size < to_size:
            size_text = "smaller"
        if from_size > to_size:
            size_text = "larger"

        from_label_text = f"{age_text} & {size_text}"
        if age_text != "( same time )" or size_text != "( same size )":
            from_label_text = f"{from_date.format('%F %R')}     {sizeof_fmt(from_size)}     ( {from_size} bytes )  ( {age_text} & {size_text} )"
        to_label_text = f"{to_date.format('%F %R')}     {sizeof_fmt(to_size)}     ( {to_size} bytes )"

        self._exists_file_diff_from.set_text(from_label_text)
        self._exists_file_diff_to.set_text(to_label_text)


    def exists_rename_field_changed(self, widget):
        nfile_name = widget.get_text().strip()
        ofile_name = self._exists_file_label.get_label()

        if nfile_name:
            if nfile_name == ofile_name:
                self._exists_file_rename_bttn.set_sensitive(False)
            else:
                self._exists_file_rename_bttn.set_sensitive(True)
        else:
            self._exists_file_rename_bttn.set_sensitive(False)
