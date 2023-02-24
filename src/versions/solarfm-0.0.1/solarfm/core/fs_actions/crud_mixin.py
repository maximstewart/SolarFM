# Python imports

# Lib imports

# Application imports




class CRUDMixin:
    """docstring for CRUDMixin"""

    def move_files(self, files, target):
        self.handle_files(files, "move", target)

    def paste_files(self):
        state     = event_system.emit_and_await("get_current_state")
        target    = f"{state.tab.get_current_directory()}"

        if self._to_copy_files:
            self.handle_files(self._to_copy_files, "copy", target)
        elif self._to_cut_files:
            self.handle_files(self._to_cut_files, "move", target)

    def create_files(self):
        fname_field     = self._builder.get_object("new_fname_field")
        cancel_creation = event_system.emit_and_await("show_new_file_menu", fname_field)

        if cancel_creation:
            event_system.emit("hide_new_file_menu")
            return

        file_name = fname_field.get_text().strip()
        type      = self._builder.get_object("new_file_toggle_type").get_state()
        state     = event_system.emit_and_await("get_current_state")
        target    = f"{state.tab.get_current_directory()}"

        if file_name:
            path = f"{target}/{file_name}"

            if type == True:     # Create File
                self.handle_files([path], "create_file")
            else:                # Create Folder
                self.handle_files([path], "create_dir")

        event_system.emit("hide_new_file_menu")

    def rename_files(self):
        rename_label = self._builder.get_object("file_to_rename_label")
        rename_input = self._builder.get_object("rename_fname")
        state        = event_system.emit_and_await("get_current_state")

        for uri in state.uris:
            entry = uri.split("/")[-1]
            rename_label.set_label(entry)
            rename_input.set_text(entry)

            response = event_system.emit_and_await("show_rename_file_menu", rename_input)
            if response == "skip_edit":
                continue
            if response == "cancel_edit":
                break

            rname_to = rename_input.get_text().strip()
            if rname_to:
                target = f"{state.tab.get_current_directory()}/{rname_to}"
                self.handle_files([uri], "rename", target)

        event_system.emit("hide_rename_file_menu")
        event_system.emit_and_await("get_selected_files").clear()
