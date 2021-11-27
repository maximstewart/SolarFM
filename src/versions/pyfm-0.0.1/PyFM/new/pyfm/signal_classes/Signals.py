# Python imports
import threading, subprocess, signal, inspect, os, time

# Gtk imports
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib

# Application imports
from .mixins import *
from shellfm import WindowController


def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()
    return wrapper


class Signals(WidgetFileActionMixin, PaneMixin, WindowMixin):
    def __init__(self, args, unknownargs, settings):
        self.settings          = settings
        self.builder           = self.settings.builder
        self.logger            = self.settings.logger

        self.window_controller = WindowController()
        self.state             = self.window_controller.load_state()

        self.window            = self.settings.getMainWindow()
        self.window1           = self.builder.get_object("window_1")
        self.window2           = self.builder.get_object("window_2")
        self.window3           = self.builder.get_object("window_3")
        self.window4           = self.builder.get_object("window_4")
        self.notebooks         = [self.window1, self.window2, self.window3, self.window4]
        self.selected_files    = []
        self.to_rename_files   = []
        self.to_copy_files     = []
        self.to_cut_files      = []

        self.single_click_open = False
        self.is_pane1_hidden   = False
        self.is_pane2_hidden   = False
        self.is_pane3_hidden   = False
        self.is_pane4_hidden   = False

        self.skip_edit         = False
        self.cancel_edit       = False
        self.ctrlDown          = False
        self.shiftDown         = False
        self.altDown           = False

        self.window.show()
        self.generate_windows(self.state)

        self.window.connect("delete-event", self.tear_down)
        GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, self.tear_down)
        self.gui_event_observer()

        if unknownargs:
            for arg in unknownargs:
                if os.path.isdir(arg):
                    message = f"FILE|{arg}"
                    event_system.send_ipc_message(message)

        if args.new_tab and os.path.isdir(args.new_tab):
            message = f"FILE|{args.new_tab}"
            event_system.send_ipc_message(message)


    def tear_down(self, widget=None, eve=None):
        event_system.monitor_events  = False
        event_system.send_ipc_message("close server")
        self.window_controller.save_state()
        time.sleep(event_sleep_time)
        Gtk.main_quit()


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
        store, tab_label = self.get_store_and_label_from_notebook(notebook, f"{wid}|{tid}")
        view      = self.get_fm_window(wid).get_view_by_id(tid)

        view.load_directory()
        self.load_store(view, store)

    def has_method(self, o, name):
        return callable(getattr(o, name, None))


    def do_action_from_menu_controls(self, imagemenuitem, eventbutton):
        action        = imagemenuitem.get_name()
        self.ctrlDown = True
        self.hide_context_menu()
        self.hide_new_file_menu()
        self.hide_edit_file_menu()

        if action == "create":
            self.create_file()
            self.hide_new_file_menu()
        if action == "open":
            self.open_files()
        if action == "rename":
            self.to_rename_files = self.selected_files
            self.rename_files()
        if action == "cut":
            self.to_copy_files.clear()
            self.cut_files()
        if action == "copy":
            self.to_cut_files.clear()
            self.copy_files()
        if action == "paste":
            self.paste_files()
        if action == "delete":
            # self.delete_files()
            self.trash_files()
        if action == "trash":
            self.trash_files()

        self.ctrlDown = False


    def global_key_press_controller(self, eve, user_data):
        keyname = Gdk.keyval_name(user_data.keyval).lower()
        if "control" in keyname or "alt" in keyname or "shift" in keyname:
            if "control" in keyname:
                self.ctrlDown    = True
            if "shift" in keyname:
                self.shiftDown   = True
            if "alt" in keyname:
                self.altDown = True

    # NOTE: Yes, this should actually be mapped to some key controller setting
    #       file or something. Sue me.
    def global_key_release_controller(self, eve, user_data):
        keyname = Gdk.keyval_name(user_data.keyval).lower()
        if debug:
            print(f"global_key_release_controller > key > {keyname}")

        if "control" in keyname or "alt" in keyname or "shift" in keyname:
            if "control" in keyname:
                self.ctrlDown    = False
            if "shift" in keyname:
                self.shiftDown   = False
            if "alt" in keyname:
                self.altDown     = False

        if self.ctrlDown and keyname == "q":
            self.tear_down()
        if (self.ctrlDown and keyname == "slash") or keyname == "home":
            self.builder.get_object("go_home").released()
        if self.ctrlDown and keyname == "r":
            self.builder.get_object("refresh_view").released()
        if (self.ctrlDown and keyname == "up") or (self.ctrlDown and keyname == "u"):
            self.builder.get_object("go_up").released()
        if self.ctrlDown and keyname == "l":
            self.builder.get_object("path_entry").grab_focus()
        if self.ctrlDown and keyname == "t":
            self.builder.get_object("create_tab").released()
        if self.ctrlDown and keyname == "o":
            self.open_files()
        if self.ctrlDown and keyname == "w":
            self.keyboard_close_tab()
        if self.ctrlDown and keyname == "h":
            self.show_hide_hidden_files()
        if (self.ctrlDown and keyname == "e"):
            self.edit_files()
        if self.ctrlDown and keyname == "c":
            self.to_cut_files.clear()
            self.copy_files()
        if self.ctrlDown and keyname == "x":
            self.to_copy_files.clear()
            self.cut_files()
        if self.ctrlDown and keyname == "v":
            self.paste_files()
        if self.ctrlDown and keyname == "n":
            self.show_new_file_menu()

        if keyname == "delete":
            self.trash_files()
        if keyname == "f2":
            self.to_rename_files = self.selected_files
            self.rename_files()
        if keyname == "f4":
            wid, tid = self.window_controller.get_active_data()
            view     = self.get_fm_window(wid).get_view_by_id(tid)
            dir      = view.get_current_directory()
            self.execute("terminator", dir)


    def execute(self, option, start_dir=os.getenv("HOME")):
        DEVNULL = open(os.devnull, 'w')
        command = option.split()
        subprocess.Popen(command, cwd=start_dir, start_new_session=True, stdout=DEVNULL, stderr=DEVNULL)




    def show_about_page(self, widget, eve):
        about_page = self.builder.get_object("about_page")
        response   = about_page.run()
        if response == -4:
            self.hide_about_page()

    def hide_about_page(self, widget=None, eve=None):
        about_page = self.builder.get_object("about_page").hide()


    def show_appchooser_menu(self, widget=None, eve=None):
        appchooser_menu   = self.builder.get_object("appchooser_menu")
        appchooser_widget = self.builder.get_object("appchooser_widget")

        resp = appchooser_menu.run()
        if resp == Gtk.ResponseType.CANCEL:
            self.hide_appchooser_menu()
        if resp == Gtk.ResponseType.OK:
            self.open_with_files(appchooser_widget)
            self.hide_appchooser_menu()

    def hide_appchooser_menu(self, widget=None, eve=None):
        self.builder.get_object("appchooser_menu").hide()

    def run_appchooser_launch(self, widget=None, eve=None):
        self.builder.get_object("appchooser_select_btn").pressed()

    def show_context_menu(self, widget=None, eve=None):
        self.builder.get_object("context_menu").run()

    def hide_context_menu(self, widget=None, eve=None):
        self.builder.get_object("context_menu").hide()

    def show_new_file_menu(self, widget=None, eve=None):
        self.builder.get_object("new_file_menu").run()

    def hide_new_file_menu(self, widget=None, eve=None):
        self.builder.get_object("new_file_menu").hide()

    def show_edit_file_menu(self, widget=None, eve=None):
        self.builder.get_object("edit_file_menu").run()

    def hide_edit_file_menu(self, widget=None, eve=None):
        self.builder.get_object("edit_file_menu").hide()

    def hide_edit_file_menu_skip(self, widget=None, eve=None):
        self.skip_edit   = True
        self.builder.get_object("edit_file_menu").hide()

    def hide_edit_file_menu_cancel(self, widget=None, eve=None):
        self.cancel_edit = True
        self.builder.get_object("edit_file_menu").hide()





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


    # def getClipboardData(self):
    #     proc    = subprocess.Popen(['xclip','-selection', 'clipboard', '-o'], stdout=subprocess.PIPE)
    #     retcode = proc.wait()
    #     data    = proc.stdout.read()
    #     return data.decode("utf-8").strip()
    #
    # def setClipboardData(self, data):
    #     proc = subprocess.Popen(['xclip','-selection','clipboard'], stdin=subprocess.PIPE)
    #     proc.stdin.write(data)
    #     proc.stdin.close()
    #     retcode = proc.wait()
