# Python imports
import base64

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Application imports


class GrepPreviewWidget(Gtk.Box):
    def __init__(self, _path, sub_keys, data):
        super(GrepPreviewWidget, self).__init__()
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.line_color = "#e0cc64"

        path   = base64.urlsafe_b64decode(_path.encode('utf-8')).decode('utf-8')
        _label = '/'.join( path.split("/")[-3:] )
        title  = Gtk.LinkButton.new_with_label(uri=f"file://{path}", label=_label)

        self.add(title)
        for key in sub_keys:
            line_num     = key
            text = base64.urlsafe_b64decode(data[key].encode('utf-8')).decode('utf-8')


            box          = Gtk.Box()
            number_label = Gtk.Label()
            text_view    = Gtk.Label(label=text[:-1])
            label_text   = f"<span foreground='{self.line_color}'>{line_num}</span>"

            number_label.set_markup(label_text)
            number_label.set_margin_left(15)
            number_label.set_margin_right(5)
            number_label.set_margin_top(5)
            number_label.set_margin_bottom(5)
            text_view.set_margin_top(5)
            text_view.set_margin_bottom(5)
            text_view.set_line_wrap(True)

            box.add(number_label)
            box.add(text_view)
            self.add(box)

        self.show_all()
