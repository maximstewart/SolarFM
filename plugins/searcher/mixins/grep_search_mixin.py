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
from ..widgets.grep_preview_widget import GrepPreviewWidget


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


class GrepSearchMixin:
    def _run_grep_query(self, widget=None, eve=None):
        self._queue_grep = True

        if not self._grep_watcher_running:
            self._grep_watcher_running = True

            self._stop_grep_query()
            self.reset_grep_box()
            self.run_grep_watcher(query=widget)

    @daemon_threaded
    def run_grep_watcher(self, query):
        while True:
            if self._queue_grep:
                self._queue_grep = False
                time.sleep(1)

                # NOTE: Hold call to translate if we're still typing/updating...
                if self._queue_grep:
                    continue

                # NOTE: If query create new process and do all new loop.
                if query:
                    self.pause_fifo_update = False
                    GLib.idle_add(self._exec_grep_query, query)

                self._grep_watcher_running = False

            break

    def _stop_grep_query(self, widget=None, eve=None):
        self._spinner.stop()

        # NOTE: Freeze IPC consumption
        self.pause_fifo_update = True
        self.grep_query        = ""
        dt                     = datetime.now()
        self.grep_time_stamp   = datetime.timestamp(dt) # NOTE: Get timestamp

        # NOTE: Kill the former process
        if self._grep_proc:
            if self._grep_proc.poll() == None:
                self._grep_proc.terminate()
                while self._grep_proc.poll() == None:
                    ...

            self._grep_proc = None


    def _exec_grep_query(self, widget=None, eve=None):
        query = widget.get_text()

        if not query.strip() in ("", None):
            self.grep_query = query

            target_dir = shlex.quote( self._fm_state.tab.get_current_directory() )
            command = ["python", f"{self.path}/utils/search.py", "-t", "grep_search", "-d", f"{target_dir}", "-q", f"{query}"]
            self._spinner.start()
            self._grep_proc = subprocess.Popen(command, cwd=self.path, stdin=None, stdout=None, stderr=None)

    def _load_grep_ui(self, data):
        Gtk.main_iteration()

        if not data in ("", None):
            jdata = json.loads( data )
            jkeys = jdata.keys()
            for key in jkeys:
                sub_keys    = jdata[key].keys()
                grep_result = jdata[key]

                widget = GrepPreviewWidget(key, sub_keys, grep_result, self.grep_query)
                self._grep_list.add(widget)
