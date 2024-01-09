# Python imports
import os
import json
import inspect

# Lib imports

# Application imports




class StartCheckMixin:
    def is_dirty_start(self) -> bool:
        return self._dirty_start

    def clear_pid(self):
        if not self.is_trace_debug():
            self._clean_pid()

    def do_dirty_start_check(self):
        if self.is_trace_debug():
            pid = os.getpid()
            self._print_pid(pid)
            return

        if os.path.exists(self._PID_FILE):
            with open(self._PID_FILE, "r") as f:
                pid = f.readline().strip()
                if pid not in ("", None):
                    if self.is_pid_alive( int(pid) ):
                        print("PID file exists and PID is alive... Letting downstream errors (sans debug args) handle app closure propigation.")
                        return

        self._write_new_pid()

    """ Check For the existence of a unix pid. """
    def is_pid_alive(self, pid):
        print(f"PID Found: {pid}")

        try:
            os.kill(pid, 0)
        except OSError:
            print(f"{app_name} PID file exists but PID is irrelevant; starting dirty...")
            self._dirty_start = True
            return False

        return True

    def _write_new_pid(self):
        pid = os.getpid()
        self._write_pid(pid)
        self._print_pid(pid)

    def _print_pid(self, pid):
        print(f"{app_name} PID:  {pid}")

    def _clean_pid(self):
        os.unlink(self._PID_FILE)

    def _write_pid(self, pid):
        with open(self._PID_FILE, "w") as _pid:
            _pid.write(f"{pid}")