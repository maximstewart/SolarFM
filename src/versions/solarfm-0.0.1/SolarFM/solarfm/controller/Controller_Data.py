# Python imports
import sys, os, signal

# Lib imports
from gi.repository import GLib

# Application imports
from trasher.xdgtrash import XDGTrash
from shellfm import WindowController
from plugins import Plugins




class Controller_Data:
    ''' Controller_Data contains most of the state of the app at ay given time. It also has some support methods. '''

    def setup_controller_data(self, _settings):
        self.trashman           = XDGTrash()
        self.window_controller  = WindowController()
        self.plugins            = Plugins(_settings)
        self.state              = self.window_controller.load_state()
        self.trashman.regenerate()

        self.settings           = _settings
        self.builder            = self.settings.get_builder()
        self.logger             = self.settings.get_logger()

        self.window             = self.settings.get_main_window()
        self.window1            = self.builder.get_object("window_1")
        self.window2            = self.builder.get_object("window_2")
        self.window3            = self.builder.get_object("window_3")
        self.window4            = self.builder.get_object("window_4")
        self.message_widget     = self.builder.get_object("message_widget")
        self.message_view       = self.builder.get_object("message_view")
        self.message_buffer     = self.builder.get_object("message_buffer")
        self.arc_command_buffer = self.builder.get_object("arc_command_buffer")

        self.exists_file_rename_bttn = self.builder.get_object("exists_file_rename_bttn")
        self.warning_alert      = self.builder.get_object("warning_alert")
        self.edit_file_menu     = self.builder.get_object("edit_file_menu")
        self.file_exists_dialog = self.builder.get_object("file_exists_dialog")
        self.exists_file_label  = self.builder.get_object("exists_file_label")
        self.exists_file_field  = self.builder.get_object("exists_file_field")
        self.path_menu          = self.builder.get_object("path_menu")
        self.path_entry         = self.builder.get_object("path_entry")

        self.bottom_size_label       = self.builder.get_object("bottom_size_label")
        self.bottom_file_count_label = self.builder.get_object("bottom_file_count_label")
        self.bottom_path_label       = self.builder.get_object("bottom_path_label")

        self.trash_files_path        = GLib.get_user_data_dir() + "/Trash/files"
        self.trash_info_path         = GLib.get_user_data_dir() + "/Trash/info"

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

        self.notebooks         = [self.window1, self.window2, self.window3, self.window4]
        self.selected_files    = []
        self.to_copy_files     = []
        self.to_cut_files      = []

        self.single_click_open = False
        self.is_pane1_hidden   = False
        self.is_pane2_hidden   = False
        self.is_pane3_hidden   = False
        self.is_pane4_hidden   = False

        self.override_drop_dest = None
        self.is_searching       = False
        self.search_iconview    = None
        self.search_view        = None

        self.skip_edit         = False
        self.cancel_edit       = False
        self.ctrlDown          = False
        self.shiftDown         = False
        self.altDown           = False

        self.success           = "#88cc27"
        self.warning           = "#ffa800"
        self.error             = "#ff0000"

        sys.excepthook = self.custom_except_hook
        self.window.connect("delete-event", self.tear_down)
        GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, self.tear_down)

    def get_current_state(self):
        '''
        Returns the state info most useful for any given context and action intent.

                Parameters:
                        a (obj): self

                Returns:
                        wid, tid, view, iconview, store
        '''
        wid, tid     = self.window_controller.get_active_data()
        view         = self.get_fm_window(wid).get_view_by_id(tid)
        iconview     = self.builder.get_object(f"{wid}|{tid}|iconview")
        store        = iconview.get_model()
        return wid, tid, view, iconview, store


    def clear_console(self):
        ''' Clears the terminal screen. '''
        os.system('cls' if os.name == 'nt' else 'clear')

    def call_method(self, _method_name, data = None):
        '''
        Calls a method from scope of class.

                Parameters:
                        a (obj): self
                        b (str): method name to be called
                        c (*): Data (if any) to be passed to the method.
                                Note: It must be structured according to the given methods requirements.

                Returns:
                        Return data is that which the calling method gives.
        '''
        method_name = str(_method_name)
        method      = getattr(self, method_name, lambda data: f"No valid key passed...\nkey={method_name}\nargs={data}")
        return method(data) if data else method()

    def has_method(self, obj, name):
        ''' Checks if a given method exists. '''
        return callable(getattr(obj, name, None))

    def clear_children(self, widget):
        ''' Clear children of a gtk widget. '''
        for child in widget.get_children():
            widget.remove(child)
