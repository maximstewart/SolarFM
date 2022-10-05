# Python imports
import threading, subprocess, signal, time, json, shlex

# Lib imports
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
        self._handle_find_file_query(query=widget)

    @daemon_threaded
    def _handle_find_file_query(self, widget=None, eve=None, query=None):
        # NOTE: Freeze IPC consumption
        self.pause_fifo_update = True
        self.search_query      = ""

        # NOTE: Kill the former process
        if self._list_proc:
            if self._list_proc.poll():
                self._list_proc.send_signal(signal.SIGKILL)
                while self._list_proc.poll():
                    pass

                self._list_proc = None
            else:
                self._list_proc = None

        # NOTE: Clear children from ui and make sure ui thread redraws
        GLib.idle_add(self.clear_children, self._file_list)
        while len(self._file_list.get_children()) > 0:
            time.sleep(0.2)

        # NOTE: If query create new process and do all new loop.
        self.pause_fifo_update = False
        if query:
            GLib.idle_add(self._exec_find_file_query, query)

    def _exec_find_file_query(self, widget=None, eve=None):
        query = widget.get_text()

        if not query in ("", None):
            self.search_query = query
            target_dir = shlex.quote( self._fm_state.tab.get_current_directory() )
            command = ["python", f"{self.path}/utils/search.py", "-t", "file_search", "-d", f"{target_dir}", "-q", f"{query}"]
            self._list_proc = subprocess.Popen(command, cwd=self.path, stdin=None, stdout=None, stderr=None)

    def _load_file_ui(self, data):
        if self.pause_fifo_update:
            return

        if not data in ("", None):
            jdata  = json.loads( data )
            target = jdata[0]
            file   = jdata[1]

            widget = FilePreviewWidget(target, file)
            self._file_list.add(widget)
