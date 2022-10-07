# Python imports
import threading, subprocess, signal, time, json, shlex

# Lib imports
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
        self._handle_grep_query(query=widget)

    # TODO: Merge this logic with nearly the exact same thing in file_search_mixin
    @daemon_threaded
    def _handle_grep_query(self, widget=None, eve=None, query=None):
        # NOTE: Freeze IPC consumption
        self.pause_fifo_update = True
        self.grep_query        = ""

        # NOTE: Kill the former process
        if self._grep_proc:
            if self._grep_proc.poll() == None:
                self._grep_proc.terminate()
                while self._grep_proc.poll() == None:
                    ...

            self._grep_proc = None

        # NOTE: Clear children from ui and make sure ui thread redraws
        GLib.idle_add(self.reset_grep_box)

        # NOTE: If query create new process and do all new loop.
        self.pause_fifo_update = False
        if query:
            GLib.idle_add(self._exec_grep_query, query)

    def _exec_grep_query(self, widget=None, eve=None):
        query = widget.get_text()
        if not query in ("", None):
            self.grep_query = query

            target_dir = shlex.quote( self._fm_state.tab.get_current_directory() )
            command = ["python", f"{self.path}/utils/search.py", "-t", "grep_search", "-d", f"{target_dir}", "-q", f"{query}"]
            self._grep_proc = subprocess.Popen(command, cwd=self.path, stdin=None, stdout=None, stderr=None)

    def _load_grep_ui(self, data):
        if not data in ("", None):
            jdata = json.loads( data )
            jkeys = jdata.keys()
            for key in jkeys:
                sub_keys    = jdata[key].keys()
                grep_result = jdata[key]

                widget = GrepPreviewWidget(key, sub_keys, grep_result, self.grep_query)
                self._grep_list.add(widget)
