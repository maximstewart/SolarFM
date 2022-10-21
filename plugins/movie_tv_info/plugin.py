# Python imports
import os, threading, subprocess, inspect, requests, shutil

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import Gtk, GLib, GdkPixbuf

# Application imports
from plugins.plugin_base import PluginBase
from .tmdbscraper import scraper


# NOTE: Threads WILL NOT die with parent's destruction.
def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs, daemon=False).start()
    return wrapper

# NOTE: Threads WILL die with parent's destruction.
def daemon_threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs, daemon=True).start()
    return wrapper




class Plugin(PluginBase):
    def __init__(self):
        super().__init__()

        self.path                   = os.path.dirname(os.path.realpath(__file__))
        self.name                   = "Movie/TV Info"   # NOTE: Need to remove after establishing private bidirectional 1-1 message bus
                                                        #       where self.name should not be needed for message comms
        self._GLADE_FILE            = f"{self.path}/movie_tv_info.glade"

        self._dialog                = None
        self._thumbnail_preview_img = None
        self._tmdb                  = scraper.get_tmdb_scraper()
        self._overview              = None
        self._file_name             = None
        self._file_location         = None
        self._trailer_link          = None


    def run(self):
        self._builder           = Gtk.Builder()
        self._builder.add_from_file(self._GLADE_FILE)

        classes  = [self]
        handlers = {}
        for c in classes:
            methods = None
            try:
                methods = inspect.getmembers(c, predicate=inspect.ismethod)
                handlers.update(methods)
            except Exception as e:
                print(repr(e))

        self._builder.connect_signals(handlers)

        self._thumbnailer_dialog    = self._builder.get_object("info_dialog")
        self._overview              = self._builder.get_object("textbuffer")
        self._file_name             = self._builder.get_object("file_name")
        self._file_location         = self._builder.get_object("file_location")
        self._thumbnail_preview_img = self._builder.get_object("thumbnail_preview_img")
        self._file_hash             = self._builder.get_object("file_hash")
        self._trailer_link          = self._builder.get_object("trailer_link")

    def generate_reference_ui_element(self):
        icon   = Gtk.Image(stock=Gtk.STOCK_FIND)
        button = Gtk.Button(label=self.name)

        button.connect("button-release-event", self._show_info_page)
        button.set_image(icon)

        return button

    @threaded
    def _show_info_page(self, widget=None, eve=None):
        self._event_system.emit("get_current_state")

        state               = self._fm_state
        self._event_message = None

        GLib.idle_add(self._process_changes, (state))

    def _process_changes(self, state):
        self._fm_state = None

        if len(state.selected_files) == 1:
            self._fm_state = state
            self._set_ui_data()
            response   = self._thumbnailer_dialog.run()
            if response in [Gtk.ResponseType.CLOSE, Gtk.ResponseType.DELETE_EVENT]:
                self._thumbnailer_dialog.hide()

    def _set_ui_data(self):
        title, path, trailer, video_data = self.get_video_data()
        keys = video_data.keys() if video_data else None

        overview_text  = video_data["overview"] if video_data else f"...NO {self.name.upper()} DATA..."

        self.set_text_data(title, path, overview_text)
        self.set_thumbnail(video_data) if video_data else ...
        self.set_trailer_link(trailer)

        print(video_data["videos"]) if not keys in ("", None) and "videos" in keys else ...

    def get_video_data(self):
        uri            = self._fm_state.selected_files[0]
        path           = self._fm_state.tab.get_current_directory()
        parts          = uri.split("/")
        _title         = parts[ len(parts) - 1 ]
        trailer        = None

        try:
            title          = _title.split("(")[0].strip()
            startIndex     = _title.index('(') + 1
            endIndex       = _title.index(')')
            date           = title[startIndex:endIndex]
        except Exception as e:
            print(repr(e))
            title          = _title
            date           = None

        try:

            video_data    = self._tmdb.search(title, date)[0]
            video_id      = video_data["id"]
            try:
                results = self._tmdb.tmdbapi.get_movie(str(video_id), append_to_response="videos")["videos"]["results"]
                for result in results:
                    if "YouTube" in result["site"]:
                        trailer = result["key"]

                if not trailer:
                    raise Exception("No key found. Defering to none...")
            except Exception as e:
                print("No trailer found...")

        except Exception as e:
            print(repr(e))
            video_data    = None

        return title, path, trailer, video_data


    def set_text_data(self, title, path, overview_text):
        self._file_name.set_text(title)
        self._file_location.set_text(path)
        self._overview.set_text(overview_text)

    @threaded
    def set_thumbnail(self, video_data):
        background_url = video_data["backdrop_path"]
        # background_url = video_data["poster_path"]
        background_pth = "/tmp/sfm_mvtv_info.jpg"

        try:
            os.remove(background_pth)
        except Exception as e:
            ...

        r = requests.get(background_url, stream = True)

        if r.status_code == 200:
            r.raw.decode_content = True
            with open(background_pth,'wb') as f:
                shutil.copyfileobj(r.raw, f)

            print('Cover Background Image sucessfully retreived...')
            preview_pixbuf = GdkPixbuf.Pixbuf.new_from_file(background_pth)
            self._thumbnail_preview_img.set_from_pixbuf(preview_pixbuf)
        else:
            print('Cover Background Image Couldn\'t be retreived...')

    def set_trailer_link(self, trailer):
        if trailer:
            self._trailer_link.set_uri(f"https://www.youtube.com/watch?v={trailer}")
