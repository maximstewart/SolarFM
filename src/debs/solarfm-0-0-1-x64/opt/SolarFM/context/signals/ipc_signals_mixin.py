# Python imports

# Lib imports

# Application imports


class IPCSignalsMixin:
    """ IPCSignalsMixin handle messages from another starting solarfm process. """

    def print_to_console(self, message=None):
        print(self)
        print(message)

    def handle_file_from_ipc(self, path):
        wid, tid   = self.window_controller.get_active_wid_and_tid()
        notebook   = self.builder.get_object(f"window_{wid}")
        if notebook.is_visible():
            self.create_tab(wid, path)
            return

        if not self.is_pane4_hidden:
            self.create_tab(4, path)
        elif not self.is_pane3_hidden:
            self.create_tab(3, path)
        elif not self.is_pane2_hidden:
            self.create_tab(2, path)
        elif not self.is_pane1_hidden:
            self.create_tab(1, path)
