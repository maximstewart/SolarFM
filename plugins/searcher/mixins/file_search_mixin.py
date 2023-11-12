# Python imports
import time
import threading
import subprocess
import signal
import json
import shlex
from datetime import datetime

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GLib

# Application imports
from ..widgets.file_preview_widget import FilePreviewWidget


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


class FileSearchMixin:
    def _run_find_file_query(self, widget=None, eve=None):
        self._queue_search = True

        if not self._search_watcher_running:
            self._search_watcher_running = True

            self._stop_fsearch_query()
            self.reset_file_list_box()
            self.run_fsearch_watcher(query=widget)








# Need to implement this over the threaded stuffs....


    def cancel_timer(self):
		if self.timer:
			self.timer.cancel()
			GLib.idle_remove_by_data(None)

	def delay_search_Glib(self):
		GLib.idle_add(self._do_highlight)

	def delay_search(self):
		wait_time = self.search_time / len(self.search_text)
		wait_time = max(wait_time, 0.05)

		self.timer = threading.Timer(wait_time, self.delay_search_Glib)
		self.timer.daemon = True
		self.timer.start()



















    @daemon_threaded
    def run_fsearch_watcher(self, query):
        while True:
            if self._queue_search:
                self._queue_search = False
                time.sleep(1)

                # NOTE: Hold call to translate if we're still typing/updating...
                if self._queue_search:
                    continue

                # NOTE: If query create new process and do all new loop.
                if query:
                    self.pause_fifo_update = False
                    GLib.idle_add(self._exec_find_file_query, query)

                self._search_watcher_running = False

            break

    def _stop_fsearch_query(self, widget=None, eve=None):
        self._spinner.stop()

        # NOTE: Freeze IPC consumption
        self.pause_fifo_update  = True
        self.search_query       = ""
        dt                      = datetime.now()
        self.fsearch_time_stamp = datetime.timestamp(dt) # NOTE: Get timestamp

        # NOTE: Kill the former process
        if self._list_proc:
            if self._list_proc.poll() == None:
                self._list_proc.terminate()
                while self._list_proc.poll() == None:
                    ...

            self._list_proc = None


    def _exec_find_file_query(self, widget=None, eve=None):
        query = widget.get_text()

        if not query in ("", None):
            self.search_query = query
            target_dir        = shlex.quote( self._fm_state.tab.get_current_directory() )
            command           = ["python", f"{self.path}/utils/search.py", "-t", "file_search", "-d", f"{target_dir}", "-q", f"{query}"]

            self._spinner.start()

            self._list_proc = subprocess.Popen(command, cwd=self.path, stdin=None, stdout=None, stderr=None)


    def _load_file_ui(self, data):
        Gtk.main_iteration()

        if not data in ("", None):
            jdata  = json.loads( data )
            target = jdata[0]
            file   = jdata[1]

            widget = FilePreviewWidget(target, file)
            self._file_list.add(widget)