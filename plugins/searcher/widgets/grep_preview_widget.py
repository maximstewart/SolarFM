# Python imports
import base64

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Application imports


class GrepPreviewWidget(Gtk.Box):
    def __init__(self, _path, sub_keys, _data):
        super(GrepPreviewWidget, self).__init__()
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.line_color = "#e0cc64"

        path      = self.decode_str(_path)
        _label    = '/'.join( path.split("/")[-3:] )
        title     = Gtk.LinkButton.new_with_label(uri=f"file://{path}", label=_label)

        text_view = Gtk.TextView()
        text_view.set_editable(False)
        text_view.set_wrap_mode(Gtk.WrapMode.NONE)
        buffer    = text_view.get_buffer()

        for i, key in enumerate(sub_keys):
            line_num = self.make_utf8_line_num(self.line_color, key)
            text     = f"\t\t{ self.decode_str(_data[key]) }"

            itr      = buffer.get_end_iter()
            buffer.insert_markup(itr, line_num, len(line_num))
            itr      = buffer.get_end_iter()
            buffer.insert(itr, text, length=len(text))

        self.add(title)
        self.add(text_view)
        self.show_all()

    def decode_str(self, target):
        return base64.urlsafe_b64decode(target.encode('utf-8')).decode('utf-8')

    def make_utf8_line_num(self, color, target):
        return bytes(f"\n<span foreground='{color}'>{target}</span>", "utf-8").decode("utf-8")
