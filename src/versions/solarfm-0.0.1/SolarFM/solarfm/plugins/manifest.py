# Python imports
import os, json
from os.path import join

# Lib imports

# Application imports




class ManifestProcessorException(Exception):
    ...


class PluginInfo:
    path: str       = None
    name: str       = None
    author: str     = None
    version: str    = None
    support: str    = None
    requests:{}     = None
    reference: type = None


class ManifestProcessor:
    def __init__(self, path, builder):
        manifest = join(path, "manifest.json")
        if not os.path.exists(manifest):
            raise ManifestProcessorException("Invalid Plugin Structure: Plugin doesn't have 'manifest.json'. Aboarting load...")

        self._path    = path
        self._builder = builder
        with open(manifest) as f:
            data           = json.load(f)
            self._manifest = data["manifest"]
            self._plugin   = self.collect_info()

    def collect_info(self) -> PluginInfo:
        plugin          = PluginInfo()
        plugin.path     = self._path
        plugin.name     = self._manifest["name"]
        plugin.author   = self._manifest["author"]
        plugin.version  = self._manifest["version"]
        plugin.support  = self._manifest["support"]
        plugin.requests = self._manifest["requests"]

        return plugin

    def get_loading_data(self):
        loading_data = {}
        requests     = self._plugin.requests
        keys         = requests.keys()

        if "ui_target" in keys:
            if requests["ui_target"] in  [
                                            "none", "other", "main_Window", "main_menu_bar",
                                            "main_menu_bttn_box_bar", "path_menu_bar", "plugin_control_list",
                                            "context_menu", "window_1", "window_2", "window_3", "window_4"
                                        ]:
                if requests["ui_target"] == "other":
                    if "ui_target_id" in keys:
                        loading_data["ui_target"] = self._builder.get_object(requests["ui_target_id"])
                        if loading_data["ui_target"] == None:
                            raise ManifestProcessorException('Invalid "ui_target_id" given in requests. Must have one if setting "ui_target" to "other"...')
                    else:
                        raise ManifestProcessorException('Invalid "ui_target_id" given in requests. Must have one if setting "ui_target" to "other"...')
                else:
                    loading_data["ui_target"] = self._builder.get_object(requests["ui_target"])
            else:
                raise ManifestProcessorException('Unknown "ui_target" given in requests.')

        if "pass_fm_events" in keys:
            if requests["pass_fm_events"] in ["true"]:
                loading_data["pass_fm_events"] = True

        if "pass_ui_objects" in keys:
            if len(requests["pass_ui_objects"]) > 0:
                loading_data["pass_ui_objects"] = []
                for ui_id  in requests["pass_ui_objects"]:
                    try:
                        loading_data["pass_ui_objects"].append( self._builder.get_object(ui_id) )
                    except Exception as e:
                        print(repr(e))

        if "bind_keys" in keys:
            if isinstance(requests["bind_keys"], list):
                loading_data["bind_keys"] = requests["bind_keys"]

        return self._plugin, loading_data
