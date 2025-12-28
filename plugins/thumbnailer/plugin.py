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
        self._event_system.subscribe("create-video-thumbnail", self.create_video_thumbnail)
        self._event_system.subscribe("create-scaled-image", self.create_scaled_image)
        self._event_system.subscribe("get-thumbnail-hash", self.get_thumbnail_hash)
        self._event_system.subscribe("get-thumbnails-path", self.get_thumbnails_path)

    def generate_reference_ui_element(self):
        ...

    def create_thumbnail(self, dir, file) -> str:
        return self.icon_controller.create_icon(dir, file)

    def create_video_thumbnail(self, file, scrub_percent, replace):
        return self.icon_controller.create_video_thumbnail(file, scrub_percent, replace)

    def create_scaled_image(self, hash_img_pth):
        return self.icon_controller.create_scaled_image(hash_img_pth)

    def get_thumbnail_hash(self, file):
        return self.icon_controller.generate_hash_and_path(file)

    def get_thumbnails_path(self) -> str:
        return self.icon_controller.ABS_THUMBS_PTH

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
