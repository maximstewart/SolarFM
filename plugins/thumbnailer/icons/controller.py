# Python imports
import json
import os
from os import path

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Application imports
from .icon import Icon



class IconController(Icon):
    def __init__(self):
        CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))

        # NOTE: app_name should be defined using python 'builtins' and so too must be logger used in the various classes
        app_name_exists   = False
        try:
            app_name
            app_name_exists = True
        except Exception as e:
            ...

        APP_CONTEXT            = f"{app_name.lower()}" if app_name_exists else "shellfm"
        USR_APP_CONTEXT        = f"/usr/share/{APP_CONTEXT}"
        USER_HOME              = path.expanduser('~')
        CONFIG_PATH            = f"{USER_HOME}/.config/{APP_CONTEXT}"
        self.DEFAULT_ICONS     = f"{CONFIG_PATH}/icons"
        self.DEFAULT_ICON      = f"{self.DEFAULT_ICONS}/text.png"
        self.FFMPG_THUMBNLR    = f"{CONFIG_PATH}/ffmpegthumbnailer"    # Thumbnail generator binary
        self.BLENDER_THUMBNLR  = f"{CONFIG_PATH}/blender-thumbnailer"  # Blender thumbnail generator binary

        self.ICON_DIRS         = ["/usr/share/icons", f"{USER_HOME}/.icons" "/usr/share/pixmaps"]
        self.BASE_THUMBS_PTH   = f"{USER_HOME}/.thumbnails"
        self.ABS_THUMBS_PTH    = f"{self.BASE_THUMBS_PTH}/normal"
        self.STEAM_ICONS_PTH   = f"{self.BASE_THUMBS_PTH}/steam_icons"
        self.STEAM_CDN_URL     = ""

        if not path.isdir(self.BASE_THUMBS_PTH):
            os.mkdir(self.BASE_THUMBS_PTH)

        if not path.isdir(self.ABS_THUMBS_PTH):
            os.mkdir(self.ABS_THUMBS_PTH)

        if not path.isdir(self.STEAM_ICONS_PTH):
            os.mkdir(self.STEAM_ICONS_PTH)

        if not os.path.exists(self.DEFAULT_ICONS):
            self.DEFAULT_ICONS = f"{USR_APP_CONTEXT}/icons"
            self.DEFAULT_ICON  = f"{self.DEFAULT_ICONS}/text.png"

        CONFIG_FILE  = f"{CURRENT_PATH}/../settings.json"
        with open(CONFIG_FILE) as f:
            settings      = json.load(f)
            config        = settings["config"]

            self.container_icon_wh = config["container_icon_wh"]
            self.video_icon_wh     = config["video_icon_wh"]
            self.sys_icon_wh       = config["sys_icon_wh"]
            self.STEAM_CDN_URL     = config["steam_cdn_url"]

            # Filters
            filters = settings["filters"]
            self.fmeshs  = tuple(filters["meshs"])
            self.fcode   = tuple(filters["code"])
            self.fvideos = tuple(filters["videos"])
            self.foffice = tuple(filters["office"])
            self.fimages = tuple(filters["images"])
            self.ftext   = tuple(filters["text"])
            self.fmusic  = tuple(filters["music"])
            self.fpdf    = tuple(filters["pdf"])
