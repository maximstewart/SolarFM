# Python imports

# Gtk imports
from gi.repository import GLib

# Application imports
from shellfm import WindowController




class Controller_Data:
    def has_method(self, o, name):
        return callable(getattr(o, name, None))

    def setup_controller_data(self):
        self.window_controller  = WindowController()
        self.state              = self.window_controller.load_state()

        self.builder            = self.settings.builder
        self.logger             = self.settings.logger

        self.window             = self.settings.getMainWindow()
        self.window1            = self.builder.get_object("window_1")
        self.window2            = self.builder.get_object("window_2")
        self.window3            = self.builder.get_object("window_3")
        self.window4            = self.builder.get_object("window_4")
        self.message_widget     = self.builder.get_object("message_widget")
        self.message_view       = self.builder.get_object("message_view")
        self.message_buffer     = self.builder.get_object("message_buffer")
        self.arc_command_buffer = self.builder.get_object("arc_command_buffer")

        self.warning_alert      = self.builder.get_object("warning_alert")
        self.edit_file_menu     = self.builder.get_object("edit_file_menu")
        self.file_exists_dialog = self.builder.get_object("file_exists_dialog")
        self.exists_file_label  = self.builder.get_object("exists_file_label")
        self.exists_file_field  = self.builder.get_object("exists_file_field")
        self.exists_file_rename_bttn = self.builder.get_object("exists_file_rename_bttn")

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

        self.skip_edit         = False
        self.cancel_edit       = False
        self.ctrlDown          = False
        self.shiftDown         = False
        self.altDown           = False

        self.success           = "#88cc27"
        self.warning           = "#ffa800"
        self.error             = "#ff0000"
