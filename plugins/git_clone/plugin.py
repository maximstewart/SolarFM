# Python imports
import os
import threading
import subprocess
import time

# Lib imports
from . import pexpect
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Application imports
from plugins.plugin_base import PluginBase


# NOTE: Threads WILL NOT die with parent's destruction.
def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs, daemon=False).start()
    return wrapper



class GitClonePluginException(Exception):
    ...



class Plugin(PluginBase):
    def __init__(self):
        super().__init__()

        self.name              = "Git Clone"  # NOTE: Need to remove after establishing private bidirectional 1-1 message bus
                                              #       where self.name should not be needed for message comms
        self.path              = os.path.dirname(os.path.realpath(__file__))

    def generate_reference_ui_element(self):
        button = Gtk.Button(label=self.name)
        button.connect("button-release-event", self._do_download)
        return button

    def run(self):
        ...


    def _do_download(self, widget=None, eve=None):
        self._event_system.emit("get_current_state")

        self.get_user_and_pass()
        dir    = self._fm_state.tab.get_current_directory()
        events = {
                    '(?i)Username': self.get_user(),
                    '(?i)Password': self.get_pass()
                }

        self._download(dir, events)

    @threaded
    def _download(self, dir, _events):
        git_clone_link = self.get_clipboard_data()
        pexpect.run(f"git clone {git_clone_link}", cwd = dir, events=_events)


    def get_user_and_pass(self):
        response = self._fm_state.user_pass_dialog.run()
        if response in (-4, -6):
            raise GitClonePluginException("User canceled request...")


    def get_user(self):
        user   = self._fm_state.user_pass_dialog.user_input.get_text()
        return f"{user}\n"

    def get_pass(self):
        passwd = self._fm_state.user_pass_dialog.pass_input.get_text()
        return f"{passwd}\n"


    def get_clipboard_data(self, encoding="utf-8") -> str:
        proc    = subprocess.Popen(['xclip','-selection', 'clipboard', '-o'], stdout=subprocess.PIPE)
        retcode = proc.wait()
        data    = proc.stdout.read()
        return data.decode(encoding).strip()
