# Python imports

# Lib imports

# Application imports




# TODO: Should rewrite to try and support more windows more naturally
class PaneMixin:
    """docstring for PaneMixin"""

    def toggle_pane(self, child):
        if child.is_visible():
            child.hide()
        else:
            child.show()

    def run_flag_toggle(self, pane_index):
        tggl_button = self.builder.get_object(f"tggl_notebook_{pane_index}")
        if pane_index == 1:
            self.is_pane1_hidden = not self.is_pane1_hidden
            tggl_button.set_active(not self.is_pane1_hidden)
            return self.is_pane1_hidden
        elif pane_index == 2:
            self.is_pane2_hidden = not self.is_pane2_hidden
            tggl_button.set_active(not self.is_pane2_hidden)
            return self.is_pane2_hidden
        elif pane_index == 3:
            self.is_pane3_hidden = not self.is_pane3_hidden
            tggl_button.set_active(not self.is_pane3_hidden)
            return self.is_pane3_hidden
        elif pane_index == 4:
            self.is_pane4_hidden = not self.is_pane4_hidden
            tggl_button.set_active(not self.is_pane4_hidden)
            return self.is_pane4_hidden

    def toggle_notebook_pane(self, widget, eve=None):
        name        = widget.get_name()
        pane_index  = int(name[-1])
        master_pane = self.builder.get_object("pane_master")
        pane        = self.builder.get_object("pane_top") if pane_index in [1, 2] else self.builder.get_object("pane_bottom")

        state = self.run_flag_toggle(pane_index)
        if self.is_pane1_hidden and self.is_pane2_hidden and self.is_pane3_hidden and self.is_pane4_hidden:
            state = self.run_flag_toggle(pane_index)
            self._save_state(state, pane_index)
            return

        child = pane.get_child1() if pane_index in [1, 3] else pane.get_child2()

        self.toggle_pane(child)
        self._save_state(state, pane_index)

    def _save_state(self, state, pane_index):
        window = self.fm_controller.get_window_by_index(pane_index - 1)
        window.set_is_hidden(state)
        self.fm_controller.save_state()
