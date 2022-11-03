# Python imports
import os, threading, subprocess, inspect, shlex

# Lib imports
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

# NOTE: Threads WILL die with parent's destruction.
def daemon_threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs, daemon=True).start()
    return wrapper




class Plugin(PluginBase):
    def __init__(self):
        super().__init__()
        self.path               = os.path.dirname(os.path.realpath(__file__))
        self._GLADE_FILE        = f"{self.path}/archiver.glade"
        self.name = "Archiver"  # NOTE: Need to remove after establishing private bidirectional 1-1 message bus
                                #       where self.name should not be needed for message comms
        self._archiver_dialogue  = None
        self._arc_command_buffer = None

        # In compress commands:
        #    %n: First selected filename/dir to archive
        #    %N: All selected filenames/dirs to archive, or (with %O) a single filename
        #    %o: Resulting single archive file
        #    %O: Resulting archive per source file/directory (use changes %N meaning)
        #
        #  In extract commands:
        #    %x: Archive file to extract
        #    %g: Unique extraction target filename with optional subfolder
        #    %G: Unique extraction target filename, never with subfolder
        #
        #  In list commands:
        #      %x: Archive to list
        #
        #  Plus standard bash variables are accepted.
        self.arc_commands            = [ '$(which 7za || echo 7zr) a %o %N',
                                                                'zip -r %o %N',
                                                                'rar a -r %o %N',
                                                                'tar -cvf %o %N',
                                                                'tar -cvjf %o %N',
                                                                'tar -cvzf %o %N',
                                                                'tar -cvJf %o %N',
                                                                'gzip -c %N > %O',
                                                                'xz -cz %N > %O'
                                        ]


    def generate_reference_ui_element(self):
        self._builder           = Gtk.Builder()
        self._builder.add_from_file(self._GLADE_FILE)

        classes  = [self]
        handlers = {}
        for c in classes:
            methods = None
            try:
                methods = inspect.getmembers(c, predicate=inspect.ismethod)
                handlers.update(methods)
            except Exception as e:
                print(repr(e))

        self._builder.connect_signals(handlers)

        self._archiver_dialogue  = self._builder.get_object("archiver_dialogue")
        self._arc_command_buffer = self._builder.get_object("arc_command_buffer")

        item = Gtk.ImageMenuItem(self.name)
        item.set_image( Gtk.Image(stock=Gtk.STOCK_FLOPPY) )
        item.connect("activate", self.show_archiver_dialogue)
        item.set_always_show_image(True)
        return item


    def run(self):
        ...

    def show_archiver_dialogue(self, widget=None, eve=None):
        self._event_system.emit("get_current_state")
        state = self._fm_state

        self._archiver_dialogue.set_action(Gtk.FileChooserAction.SAVE)
        self._archiver_dialogue.set_current_folder(state.tab.get_current_directory())
        self._archiver_dialogue.set_current_name("arc.7z")

        response = self._archiver_dialogue.run()
        if response == Gtk.ResponseType.OK:
            save_target = self._archiver_dialogue.get_filename()
            self.archive_files(save_target, state)
        if (response == Gtk.ResponseType.CANCEL) or (response == Gtk.ResponseType.DELETE_EVENT):
            pass

        self._archiver_dialogue.hide()

    def archive_files(self, save_target, state):
        paths       = [shlex.quote(p) for p in state.selected_files]

        sItr, eItr  = self._arc_command_buffer.get_bounds()
        pre_command = self._arc_command_buffer.get_text(sItr, eItr, False)
        pre_command = pre_command.replace("%o", shlex.quote(save_target))
        pre_command = pre_command.replace("%N", ' '.join(paths))
        command     = f"{state.tab.terminal_app} -e {shlex.quote(pre_command)}"
        current_dir = state.tab.get_current_directory()

        state.tab.execute(shlex.split(command), start_dir=shlex.quote(current_dir))

    def set_arc_buffer_text(self, widget=None, eve=None):
        sid = widget.get_active_id()
        self._arc_command_buffer.set_text(self.arc_commands[int(sid)])
