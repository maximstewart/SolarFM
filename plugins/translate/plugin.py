# Python imports
import os
import time
import threading
import requests

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GLib

# Application imports
from plugins.plugin_base import PluginBase


# NOTE: Threads WILL die with parent's destruction.
def daemon_threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs, daemon=True).start()
    return wrapper




class Plugin(PluginBase):
    def __init__(self):
        super().__init__()
        self.path        = os.path.dirname(os.path.realpath(__file__))
        self.name        = "Translate"  # NOTE: Need to remove after establishing private bidirectional 1-1 message bus
                                        #       where self.name should not be needed for message comms
        self._GLADE_FILE = f"{self.path}/translate.glade"

        self._link       = "https://duckduckgo.com/translation.js?vqd=4-79469202070473384659389009732578528471&query=translate&to=en"
        self._headers    = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://duckduckgo.com/',
            'Content-Type': 'text/plain',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://duckduckgo.com',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache'
        }

        self._queue_translate = False
        self._watcher_running = False


    def generate_reference_ui_element(self):
        button = Gtk.Button(label=self.name)
        button.connect("button-release-event", self._show_translate_page)
        return button

    def run(self):
        self._builder = Gtk.Builder()
        self._builder.add_from_file(self._GLADE_FILE)
        self._connect_builder_signals(self, self._builder)

        self._translate_dialog = self._builder.get_object("translate_dialog")
        self._translate_from   = self._builder.get_object("translate_from")
        self._translate_to     = self._builder.get_object("translate_to")
        self._translate_from_buffer = self._builder.get_object("translate_from_buffer")
        self._translate_to_buffer   = self._builder.get_object("translate_to_buffer")
        self._detected_language_lbl = self._builder.get_object("detected_language_lbl")


    @threaded
    def _show_translate_page(self, widget=None, eve=None):
        event_system.emit("get_current_state")

        state               = self._fm_state
        self._event_message = None

        GLib.idle_add(self._show_ui, (state))

    def _show_ui(self, state):
        if state.uris and len(state.uris) == 1:
            file_name = state.uris[0].split("/")[-1]
            self._translate_from_buffer.set_text(file_name)

        response   = self._translate_dialog.run()
        if response in [Gtk.ResponseType.CLOSE, Gtk.ResponseType.CANCEL, Gtk.ResponseType.DELETE_EVENT]:
            self._translate_dialog.hide()

        self._translate_dialog.hide()

    def _pre_translate(self, widget=None, eve=None):
        self._queue_translate = True

        if not self._watcher_running:
            self._watcher_running = True
            self.run_translate_watcher()

    @daemon_threaded
    def run_translate_watcher(self):
        while True:
            if self._queue_translate:
                self._queue_translate = False
                time.sleep(1)

                # NOTE: Hold call to translate if we're still typing/updating...
                if self._queue_translate:
                    continue

                GLib.idle_add(self._translate)
                self._watcher_running = False
                break

    def _translate(self):
        start_itr, end_itr =  self._translate_from_buffer.get_bounds()
        from_translate     = self._translate_from_buffer.get_text(start_itr, end_itr, True).encode('utf-8')

        if from_translate in ("", None) or self._queue_translate:
            return

        response = requests.post(self._link, headers=self._headers, data=from_translate)
        if response.status_code == 200:
            data = response.json()
            self._translate_to_buffer.set_text(data["translated"])

            if "detected_language" in data.keys():
                self._detected_language_lbl.set_label(f"Detected Language: {data['detected_language']}")
        else:
            msg = f"Could not translate... Response Code: {response.status_code}"
            self._translate_to_buffer.set_text(msg)
            self._detected_language_lbl.set_label(f"Detected Language:")
