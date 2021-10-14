# Python imports
import threading, subprocess, os, time

# Gtk imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk as gtk

# Application imports
from .mixins import *
# from pyfm.shellfm.windows import WindowController
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

        event_system.push_gui_event(["update", "window_1", []])
        event_system.push_gui_event(["update", "window_2", []])
        event_system.push_fm_event(["update", "window_fm_1", []])
        event_system.push_fm_event(["update", "window_fm_2", []])


        self.single_click_open  = False
        self.is_pane1_hidden    = False
        self.is_pane2_hidden    = False
        self.is_pane3_hidden    = False
        self.is_pane4_hidden    = False

        self.window.show()
        self.generate_windows(self.state)

        self.window.connect("delete-event", self.tear_down)
        self.gui_event_observer()


    @threaded
    def gui_event_observer(self):
        while event_system.monitor_events:
            time.sleep(event_sleep_time)
            event = event_system.consume_gui_event()
            if event:
                print(event)


    def tear_down(self, widget, eve):
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

                for view in views:
                    self.create_new_view_notebook(None, view, i)

                if isHidden:
                    self.toggle_notebook_pane(object)
        else:
            for j in range(0, 4):
                i = j + 1
                self.window_controller.create_window()
                self.create_new_view_notebook(None, None, i)


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
