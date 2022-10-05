# Python imports
import base64, re

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Application imports


class GrepPreviewWidget(Gtk.Box):
    def __init__(self, _path, sub_keys, _data, _grep_query):
        super(GrepPreviewWidget, self).__init__()

        self.set_orientation(Gtk.Orientation.VERTICAL)
        line_color      = "#e0cc64"
        highlight_color = "#FBF719"
        grep_query      = _grep_query

        path  = self.decode_str(_path)
        lbl   = '/'.join( path.split("/")[-3:] )
        title = Gtk.LinkButton.new_with_label(uri=f"file://{path}", label=lbl)

        text_view = Gtk.TextView()
        buffer    = text_view.get_buffer()
        text_view.set_editable(False)
        text_view.set_monospace(True)
        text_view.set_wrap_mode(Gtk.WrapMode.NONE)

        for i, key in enumerate(sub_keys):
            line_num = self.make_utf8_line_num(line_color, key)
            itr      = buffer.get_end_iter()
            buffer.insert_markup(itr, line_num, len(line_num))

            decoded  = f"\t{self.decode_str(_data[key])}"
            self.make_utf8_line_highlight(buffer, itr, i, highlight_color, decoded, grep_query)

        self.add(title)
        self.add(text_view)
        self.show_all()

    def decode_str(self, target):
        return base64.urlsafe_b64decode(target.encode('utf-8')).decode('utf-8')

    def make_utf8_line_num(self, color, target):
        return bytes(f"\n<span foreground='{color}'>{target}</span>", "utf-8").decode("utf-8")

    def make_utf8_line_highlight(self, buffer, itr, i, color, target, query):
        parts = re.split(r"(" + query + ")(?i)", target.replace("\n", ""))
        for part in parts:
            itr  = buffer.get_end_iter()

            if not query.lower() == part.lower() and not query.lower() in part.lower():
                buffer.insert(itr, part, length=len(part))
            else:
                new_s = f"<span foreground='#000000' background='{color}'>{part}</span>"
                _part = bytes(new_s, "utf-8").decode("utf-8")
                buffer.insert_markup(itr, _part, len(_part))
