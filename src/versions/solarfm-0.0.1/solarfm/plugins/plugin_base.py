# Python imports
import os
import time
import inspect

# Lib imports

# Application imports


class PluginBaseException(Exception):
    ...


class PluginBase:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.name               = "Example Plugin"  # NOTE: Need to remove after establishing private bidirectional 1-1 message bus
                                                    #       where self.name should not be needed for message comms
        self._builder           = None
        self._ui_objects        = None
        self._fm_state          = None
        self._event_system      = None


    def run(self):
        """
            Must define regardless if needed and can 'pass' if plugin doesn't need it.
            Is intended to be used to setup internal signals or custom Gtk Builders/UI logic.
        """
        raise PluginBaseException("Method hasn't been overriden...")

    def generate_reference_ui_element(self):
        """
            Requests Key:  'ui_target': "plugin_control_list",
            Must define regardless if needed and can 'pass' if plugin doesn't use it.
            Must return a widget if "ui_target" is set.
        """
        raise PluginBaseException("Method hasn't been overriden...")

    def set_ui_object_collection(self, ui_objects):
        """
            Requests Key:  "pass_ui_objects": [""]
            Request reference to a UI component. Will be passed back as array to plugin.
            Must define in plugin if set and an array of valid glade UI IDs is given.
        """
        self._ui_objects = ui_objects

    def set_fm_event_system(self, fm_event_system):
        """
            Requests Key:  'pass_fm_events': "true"
            Must define in plugin if "pass_fm_events" is set to "true" string.
        """
        self._event_system = fm_event_system

    def subscribe_to_events(self):
        self._event_system.subscribe("update_state_info_plugins", self._update_fm_state_info)

    def _update_fm_state_info(self, state):
        self._fm_state = state

    def _connect_builder_signals(self, caller_class, builder):
        classes  = [caller_class]
        handlers = {}
        for c in classes:
            methods = None
            try:
                methods = inspect.getmembers(c, predicate=inspect.ismethod)
                handlers.update(methods)
            except Exception as e:
                logger.debug(repr(e))

        builder.connect_signals(handlers)

    def reload_package(self, plugin_path, module_dict_main=locals()):
        import importlib
        from pathlib import Path

        def reload_package_recursive(current_dir, module_dict):
            for path in current_dir.iterdir():
                if "__init__" in str(path) or path.stem not in module_dict:
                    continue

                if path.is_file() and path.suffix == ".py":
                    importlib.reload(module_dict[path.stem])
                elif path.is_dir():
                    reload_package_recursive(path, module_dict[path.stem].__dict__)

        reload_package_recursive(Path(plugin_path).parent, module_dict_main["module_dict_main"])


    def clear_children(self, widget: type) -> None:
        """ Clear children of a gtk widget. """
        for child in widget.get_children():
            widget.remove(child)
