# Python imports

# Gtk imports

# Application imports
from shellfm import WindowController


class Controller_Data:
    def has_method(self, o, name):
        return callable(getattr(o, name, None))

    def setup_controller_data(self):
        self.window_controller = WindowController()
        self.state             = self.window_controller.load_state()

        self.builder           = self.settings.builder
        self.logger            = self.settings.logger

        self.window            = self.settings.getMainWindow()
        self.window1           = self.builder.get_object("window_1")
        self.window2           = self.builder.get_object("window_2")
        self.window3           = self.builder.get_object("window_3")
        self.window4           = self.builder.get_object("window_4")
        self.message_widget    = self.builder.get_object("message_widget")
        self.message_label     = self.builder.get_object("message_label")

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

        self.success           = "#88cc27"
        self.warning           = "#ffa800"
        self.error             = "#ff0000"
