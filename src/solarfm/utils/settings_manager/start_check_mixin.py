# Python imports
import os
import json
import inspect

# Lib imports

# Application imports




class StartCheckMixin:
    def is_dirty_start(self) -> bool: return self._dirty_start
    def clear_pid(self): self._clean_pid()

    def do_dirty_start_check(self):
        if not os.path.exists(self._PID_FILE):
            self._write_new_pid()
        else:
            with open(self._PID_FILE, "r") as _pid:
                pid = _pid.readline().strip()
                if pid not in ("", None):
                    self._check_alive_status(int(pid))
                else:
                    self._write_new_pid()

    """ Check For the existence of a unix pid. """
    def _check_alive_status(self, pid):
        print(f"PID Found: {pid}")
        try:
            os.kill(pid, 0)
        except OSError:
            print(f"{app_name} is starting dirty...")
            self._dirty_start = True
            self._write_new_pid()
            return

        print("PID is alive... Let downstream errors (sans debug args) handle app closure propigation.")

    def _write_new_pid(self):
        pid = os.getpid()
        self._write_pid(pid)
        print(f"{app_name} PID:  {pid}")

    def _clean_pid(self):
        os.unlink(self._PID_FILE)

    def _write_pid(self, pid):
        with open(self._PID_FILE, "w") as _pid:
            _pid.write(f"{pid}")
