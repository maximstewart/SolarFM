# Python imports
import threading, subprocess, signal, inspect, os, time

# Gtk imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk as gtk
from gi.repository import GLib

# Application imports
from .mixins import *
from shellfm import WindowController



def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()
    return wrapper


class Signals(WindowMixin, PaneMixin):
    def __init__(self, settings):
        self.settings          = settings
        self.builder           = self.settings.builder
        self.logger            = self.settings.logger

        self.window_controller = WindowController()
        self.state             = self.window_controller.load_state()

        self.window            = self.builder.get_object("Main_Window")
        self.window1           = self.builder.get_object("window1")
        self.window2           = self.builder.get_object("window2")
        self.window3           = self.builder.get_object("window3")
        self.window4           = self.builder.get_object("window4")
        self.notebooks         = [self.window1, self.window2, self.window3, self.window4]

        self.single_click_open  = False
        self.is_pane1_hidden    = False
        self.is_pane2_hidden    = False
        self.is_pane3_hidden    = False
        self.is_pane4_hidden    = False

        self.window.show()
        self.generate_windows(self.state)

        self.window.connect("delete-event", self.tear_down)
        GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, self.tear_down)
        self.gui_event_observer()


    @threaded
    def gui_event_observer(self):
        while event_system.monitor_events:
            time.sleep(event_sleep_time)
            event = event_system.consume_gui_event()
            if event:
                try:
                    type, target, data = event
                    method = getattr(self.__class__, type)
                    GLib.idle_add(method, (self, data,))
                except Exception as e:
                    print(repr(e))

    def refresh_tab(data=None):
        self, ids = data
        wid, tid  = ids.split("|")
        notebook  = self.builder.get_object(f"window_{wid}")
        icon_view, tab_label = self.get_icon_view_and_label_from_notebook(notebook, f"{wid}|{tid}")
        view      = self.get_fm_window(wid).get_view_by_id(tid)
        store     = icon_view.get_model()
        view.load_directory()
        self.load_store(view, store)


    def tear_down(self, widget=None, eve=None):
        self.window_controller.save_state()
        event_system.monitor_events = False
        time.sleep(event_sleep_time)
        gtk.main_quit()

    def generate_windows(self, data = None):
        if data:
            for j, value in enumerate(data):
                i = j + 1
                isHidden = True if value[0]["window"]["isHidden"] == "True" else False
                object   = self.builder.get_object(f"tggl_notebook_{i}")
                views    = value[0]["window"]["views"]
                self.window_controller.create_window()
                object.set_active(True)

                for view in views:
                    self.create_new_view_notebook(None, i, view)

                if isHidden:
                    self.toggle_notebook_pane(object)
        else:
            for j in range(0, 4):
                i = j + 1
                self.window_controller.create_window()
                self.create_new_view_notebook(None, i, None)


    def getClipboardData(self):
        proc    = subprocess.Popen(['xclip','-selection', 'clipboard', '-o'], stdout=subprocess.PIPE)
        retcode = proc.wait()
        data    = proc.stdout.read()
        return data.decode("utf-8").strip()

    def setClipboardData(self, data):
        proc = subprocess.Popen(['xclip','-selection','clipboard'], stdin=subprocess.PIPE)
        proc.stdin.write(data)
        proc.stdin.close()
        retcode = proc.wait()
