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

    @daemon_threaded
    def _handle_grep_query(self, widget=None, eve=None, query=None):
        # NOTE: Freeze IPC consumption
        self.pause_fifo_update = True

        # NOTE: Kill the former process
        if self._grep_proc:
            if self._grep_proc.poll():
                self._grep_proc.send_signal(signal.SIGKILL)
                while self._grep_proc.poll():
                    pass

                self._grep_proc = None
            else:
                self._grep_proc = None

        # NOTE: Clear children from ui
        GLib.idle_add(self.clear_children, self._grep_list)
        while len(self._grep_list.get_children()) > 0:
            ...

        # NOTE: Make sure ui thread redraws
        time.sleep(0.5)
        self.pause_fifo_update = False

        # NOTE: If query create new process and do all new loop.
        if query:
            GLib.idle_add(self._exec_grep_query, query)

    def _exec_grep_query(self, widget=None, eve=None):
        query = widget.get_text()
        if not query in ("", None):
            target_dir = shlex.quote( self._fm_state.tab.get_current_directory() )
            command = ["python", f"{self.path}/utils/search.py", "-t", "grep_search", "-d", f"{target_dir}", "-q", f"{query}"]
            self._grep_proc = subprocess.Popen(command, cwd=self.path, stdin=None, stdout=None, stderr=None)

    def _load_grep_ui(self, data):
        if not data in ("", None) and not self.pause_fifo_update:
            jdata = json.loads( data )
            jkeys = jdata.keys()
            for key in jkeys:
                sub_keys    = jdata[key].keys()
                grep_result = jdata[key]

                widget = GrepPreviewWidget(key, sub_keys, grep_result)
                self._grep_list.add(widget)
