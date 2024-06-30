# Python imports
import os

# Lib imports

# Application imports
from plugins.plugin_base import PluginBase
from .icons.controller import IconController



class Plugin(PluginBase):
    def __init__(self):
        super().__init__()

        self.name        = "Thumbnailer"  # NOTE: Need to remove after establishing private bidirectional 1-1 message bus
                                          #       where self.name should not be needed for message comms
        # self.path        = os.path.dirname(os.path.realpath(__file__))


    def run(self):
        self.icon_controller = IconController()
        self._event_system.subscribe("create-thumbnail", self.create_thumbnail)

    def generate_reference_ui_element(self):
        ...

    def create_thumbnail(self, dir, file) -> str:
        return self.icon_controller.create_icon(dir, file)

    def get_video_icons(self, dir) -> list:
        data = []

    def get_video_icons(self) -> list:
        data    = []
        fvideos = self.icon_controller.fvideos
        vids    = [ file for file in os.path.list_dir(dir) if file.lower().endswith(fvideos) ]

        for file in vids:
            img_hash, hash_img_path = self.create_video_thumbnail(full_path = f"{dir}/{file}", returnHashInstead = True)
            data.append([img_hash, hash_img_path])

        return data

    def get_pixbuf_icon_str_combo(self, dir)  -> list:
        data = []
        for file in os.path.list_dir(dir):
            icon = self.icon_controller.create_icon(dir, file).get_pixbuf()
            data.append([icon, file])

        return data

    def get_gtk_icon_str_combo(self, dir) -> list:
        data = []
        for file in os.path.list_dir(dir):
            icon = self.icon_controller.create_icon(dir, file)
            data.append([icon, file[0]])

        return data
