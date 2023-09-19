# Python imports

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk

# Application imports
from .mixins.ui.pane_mixin import PaneMixin
from .mixins.ui.window_mixin import WindowMixin

from .widgets.files_view.files_widget import FilesWidget


class UIMixinException(Exception):
    ...


class UIMixin(PaneMixin, WindowMixin):
# class UIMixin(PaneMixin):
    def _generate_file_views(self, session_json = None):
        # self._wip_hybrid_approach_loading_process(session_json)
        self._current_loading_process(session_json)


    def _wip_hybrid_approach_loading_process(self, session_json = None):
        for session in session_json:
            self.fm_controller.create_window()
            FilesWidget().set_fm_controller(self.fm_controller)

        for session in session_json:
            nickname = session["window"]["Nickname"]
            tabs     = session["window"]["tabs"]
            isHidden = True if session["window"]["isHidden"] == "True" else False
            event_system.emit("load_files_view_state", (nickname, tabs))


    def _current_loading_process(self, session_json = None):
        if session_json:
            for j, value in enumerate(session_json):
                i = j + 1
                notebook_tggl_button = self.builder.get_object(f"tggl_notebook_{i}")
                is_hidden = True if value["window"]["isHidden"] == "True" else False
                tabs      = value["window"]["tabs"]
                self.fm_controller.create_window()
                notebook_tggl_button.set_active(True)

                if tabs:
                    for tab in tabs:
                        self.create_new_tab_notebook(None, i, tab)
                else:
                    self.create_new_tab_notebook(None, i, None)

                if is_hidden:
                    self.toggle_notebook_pane(notebook_tggl_button)

            try:
                if not self.is_pane4_hidden:
                    icon_grid = self.window4.get_children()[-1].get_children()[0]
                elif not self.is_pane3_hidden:
                    icon_grid = self.window3.get_children()[-1].get_children()[0]
                elif not self.is_pane2_hidden:
                    icon_grid = self.window2.get_children()[-1].get_children()[0]
                elif not self.is_pane1_hidden:
                    icon_grid = self.window1.get_children()[-1].get_children()[0]

                icon_grid.event(Gdk.Event().new(type=Gdk.EventType.BUTTON_RELEASE))
                icon_grid.event(Gdk.Event().new(type=Gdk.EventType.BUTTON_RELEASE))
            except UIMixinException as e:
                logger.info("\n:  The saved session might be missing window data!  :\nLocation: ~/.config/solarfm/session.json\nFix: Back it up and delete it to reset.\n")
                logger.debug(repr(e))
        else:
            for j in range(0, 4):
                i = j + 1
                self.fm_controller.create_window()
                self.create_new_tab_notebook(None, i, None)
