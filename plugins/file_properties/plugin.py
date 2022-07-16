# Python imports
import os, threading, subprocess, time, pwd, grp
from datetime import datetime

# Gtk imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gio

# Application imports


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




class Manifest:
    path: str     = os.path.dirname(os.path.realpath(__file__))
    name: str     = "Properties"
    author: str   = "ITDominator"
    version: str  = "0.0.1"
    support: str  = ""
    requests: {}  = {
        'ui_target': "context_menu",
        'pass_fm_events': "true"
    }

class Properties:
    file_uri: str      = None
    file_name: str     = None
    file_location: str = None
    file_target: str   = None
    mime_type: str     = None
    file_size: str     = None
    mtime: int         = None
    atime: int         = None
    file_owner: str    = None
    file_group: str    = None
    chmod_stat: str    = None


class Plugin(Manifest):
    def __init__(self):
        self._GLADE_FILE        = f"{self.path}/file_properties.glade"
        self._builder           = None
        self._properties_dialog = None

        self._event_system      = None
        self._event_sleep_time  = .5
        self._event_message     = None

        self._file_name         = None
        self._file_location     = None
        self._file_target       = None
        self._mime_type         = None
        self._file_size         = None
        self._mtime             = None
        self._atime             = None
        self._file_owner        = None
        self._file_group        = None

        self._chmod_map: {} = {
                                "7": "rwx",
                                "6": "rw",
                                "5": "rx",
                                "4": "r",
                                "3": "wx",
                                "2": "w",
                                "1": "x",
                                "0": ""
        }

        self._chmod_map_counter: {} = {
                                 "rwx": "7",
                                 "rw":  "6",
                                 "rx":  "5",
                                 "r":   "4",
                                 "wx":  "3",
                                 "w":   "2",
                                 "x":   "1",
                                 "":    "0"
        }


    def get_ui_element(self):
        self._builder           = Gtk.Builder()
        self._builder.add_from_file(self._GLADE_FILE)

        self._properties_dialog = self._builder.get_object("file_properties_dialog")
        self._file_name     = self._builder.get_object("file_name")
        self._file_location = self._builder.get_object("file_location")
        self._file_target   = self._builder.get_object("file_target")
        self._mime_type     = self._builder.get_object("mime_type")
        self._file_size     = self._builder.get_object("file_size")
        self._mtime         = self._builder.get_object("mtime")
        self._atime         = self._builder.get_object("atime")
        self._file_owner    = self._builder.get_object("file_owner")
        self._file_group    = self._builder.get_object("file_group")

        button = Gtk.Button(label=self.name)
        button.connect("button-release-event", self._show_properties_page)
        return button

    def set_fm_event_system(self, fm_event_system):
        self._event_system = fm_event_system

    def run(self):
        self._module_event_observer()




    @threaded
    def _show_properties_page(self, widget=None, eve=None):
        self._event_system.push_gui_event([self.name, "get_current_state", ()])
        self.wait_for_fm_message()

        state               = self._event_message
        self._event_message = None

        GLib.idle_add(self._process_changes, (state))

    def _process_changes(self, state):
        if len(state.selected_files) == 1:
            uri  = state.selected_files[0]
            path = state.tab.get_current_directory()


            properties = self._set_ui_data(uri, path)
            response   = self._properties_dialog.run()
            if response in [Gtk.ResponseType.CANCEL, Gtk.ResponseType.DELETE_EVENT]:
                self._properties_dialog.hide()

            self._update_file(properties)
            self._properties_dialog.hide()


    def _update_file(self, properties):
        chmod_stat = self._get_check_boxes()

        if chmod_stat is not properties.chmod_stat:
            try:
                print("\nNew chmod flags...")
                print(f"Old:  {''.join(properties.chmod_stat)}")
                print(f"New:  {chmod_stat}")

                command = ["chmod", f"{chmod_stat}", properties.file_uri]
                with subprocess.Popen(command, stdout=subprocess.PIPE) as proc:
                    result = proc.stdout.read().decode("UTF-8").strip()
                    print(result)
            except Exception as e:
                print(f"Couldn't chmod\nFile:  {properties.file_uri}")
                print( repr(e) )


        owner = self._file_owner.get_text()
        group = self._file_group.get_text()
        if owner is not properties.file_owner or group is not properties.file_group:
            try:
                print("\nNew owner/group flags...")
                print(f"Old:\n\tOwner: {properties.file_owner}\n\tGroup: {properties.file_group}")
                print(f"New:\n\tOwner: {owner}\n\tGroup: {group}")

                uid = pwd.getpwnam(owner).pw_uid
                gid = grp.getgrnam(group).gr_gid
                os.chown(properties.file_uri, uid, gid)
            except Exception as e:
                print(f"Couldn't chmod\nFile:  {properties.file_uri}")
                print( repr(e) )


    def _set_ui_data(self, uri, path):
        properties = Properties()
        file_info  = Gio.File.new_for_path(uri).query_info(attributes="standard::*,owner::*,time::access,time::changed",
                                                            flags=Gio.FileQueryInfoFlags.NONE,
                                                            cancellable=None)

        is_symlink               = file_info.get_attribute_as_string("standard::is-symlink")
        properties.file_uri      = uri
        properties.file_target   = file_info.get_attribute_as_string("standard::symlink-target") if is_symlink else ""
        properties.file_name     = file_info.get_display_name()
        properties.file_location = path
        properties.mime_type     = file_info.get_content_type()
        properties.file_size     = self._sizeof_fmt(file_info.get_size())
        properties.mtime         = datetime.fromtimestamp( int(file_info.get_attribute_as_string("time::changed")) ).strftime("%A, %B %d, %Y %I:%M:%S")
        properties.atime         = datetime.fromtimestamp( int(file_info.get_attribute_as_string("time::access")) ).strftime("%A, %B %d, %Y %I:%M:%S")
        properties.file_owner    = file_info.get_attribute_as_string("owner::user")
        properties.file_group    = file_info.get_attribute_as_string("owner::group")

        # NOTE: Read = 4,  Write = 2,  Exec = 1
        command = ["stat", "-c", "%a", uri]
        with subprocess.Popen(command, stdout=subprocess.PIPE) as proc:
            properties.chmod_stat = list(proc.stdout.read().decode("UTF-8").strip())
            owner  = self._chmod_map[f"{properties.chmod_stat[0]}"]
            group  = self._chmod_map[f"{properties.chmod_stat[1]}"]
            others = self._chmod_map[f"{properties.chmod_stat[2]}"]

            self._reset_check_boxes()
            self._set_check_boxes([["owner", owner], ["group", group], ["others", others]])

        self._file_name.set_text(properties.file_name)
        self._file_location.set_text(properties.file_location)
        self._file_target.set_text(properties.file_target)
        self._mime_type.set_label(properties.mime_type)
        self._file_size.set_label(properties.file_size)
        self._mtime.set_text(properties.mtime)
        self._atime.set_text(properties.atime)
        self._file_owner.set_text(properties.file_owner)
        self._file_group.set_text(properties.file_group)

        return properties




    def _get_check_boxes(self):
        perms = [[], [], []]

        for i, target in enumerate(["owner", "group", "others"]):
            for type in ["r", "w", "x"]:
                is_active = self._builder.get_object(f"{target}_{type}").get_active()
                if is_active:
                    perms[i].append(type)

        digits = []
        for perm in perms:
            digits.append(self._chmod_map_counter[ ''.join(perm) ])

        return ''.join(digits)

    def _set_check_boxes(self, targets):
        for name, target in targets:
            for type in list(target):
                obj = f"{name}_{type}"
                self._builder.get_object(obj).set_active(True)

    def _reset_check_boxes(self):
        for target in ["owner", "group", "others"]:
            for type in ["r", "w", "x"]:
                self._builder.get_object(f"{target}_{type}").set_active(False)

    def _sizeof_fmt(self, num, suffix="B"):
        for unit in ["", "K", "M", "G", "T", "Pi", "Ei", "Zi"]:
            if abs(num) < 1024.0:
                return f"{num:3.1f} {unit}{suffix}"
            num /= 1024.0
        return f"{num:.1f} Yi{suffix}"

    def wait_for_fm_message(self):
        while not self._event_message:
            pass

    @daemon_threaded
    def _module_event_observer(self):
        while True:
            time.sleep(self._event_sleep_time)
            event = self._event_system.read_module_event()
            if event:
                try:
                    if event[0] == self.name:
                        target_id, method_target, data = self._event_system.consume_module_event()

                        if not method_target:
                            self._event_message = data
                        else:
                            method = getattr(self.__class__, f"{method_target}")
                            if data:
                                data = method(*(self, *data))
                            else:
                                method(*(self,))
                except Exception as e:
                    print(repr(e))
