# Python imports
import json
import os
from os import path

# Lib imports

# Apoplication imports


class ShellFMSettingsException(Exception):
    ...



class Settings:
    logger            = None

    # NOTE: app_name should be defined using python 'builtins'
    app_name_exists   = False
    try:
        app_name
        app_name_exists = True
    except Exception as e:
        ...

    APP_CONTEXT       = f"{app_name.lower()}" if app_name_exists else "shellfm"
    USR_APP_CONTEXT   = f"/usr/share/{APP_CONTEXT}"
    USER_HOME         = path.expanduser('~')
    CONFIG_PATH       = f"{USER_HOME}/.config/{APP_CONTEXT}"
    CONFIG_FILE       = f"{CONFIG_PATH}/settings.json"
    HIDE_HIDDEN_FILES = True

    DEFAULT_ICONS     = f"{CONFIG_PATH}/icons"
    DEFAULT_ICON      = f"{DEFAULT_ICONS}/text.png"
    FFMPG_THUMBNLR    = f"{CONFIG_PATH}/ffmpegthumbnailer"    # Thumbnail generator binary
    BLENDER_THUMBNLR  = f"{CONFIG_PATH}/blender-thumbnailer"  # Blender thumbnail generator binary
    REMUX_FOLDER      = f"{USER_HOME}/.remuxs"                # Remuxed files folder

    ICON_DIRS         = ["/usr/share/icons", f"{USER_HOME}/.icons" "/usr/share/pixmaps"]
    BASE_THUMBS_PTH   = f"{USER_HOME}/.thumbnails"
    ABS_THUMBS_PTH    = f"{BASE_THUMBS_PTH}/normal"
    STEAM_ICONS_PTH   = f"{BASE_THUMBS_PTH}/steam_icons"

    if not os.path.exists(CONFIG_PATH) or not os.path.exists(CONFIG_FILE):
        msg = f"No config file located! Aborting loading ShellFM library...\nExpected: {CONFIG_FILE}"
        raise ShellFMSettingsException(msg)

    if not path.isdir(REMUX_FOLDER):
        os.mkdir(REMUX_FOLDER)

    if not path.isdir(BASE_THUMBS_PTH):
        os.mkdir(BASE_THUMBS_PTH)

    if not path.isdir(ABS_THUMBS_PTH):
        os.mkdir(ABS_THUMBS_PTH)

    if not path.isdir(STEAM_ICONS_PTH):
        os.mkdir(STEAM_ICONS_PTH)

    if not os.path.exists(DEFAULT_ICONS):
        DEFAULT_ICONS = f"{USR_APP_CONTEXT}/icons"
        DEFAULT_ICON  = f"{DEFAULT_ICONS}/text.png"

    with open(CONFIG_FILE) as f:
        settings          = json.load(f)
        config            = settings["config"]

        subpath           = config["base_of_home"]
        STEAM_CDN_URL     = config["steam_cdn_url"]
        FFMPG_THUMBNLR    = FFMPG_THUMBNLR   if config["thumbnailer_path"] == "" else config["thumbnailer_path"]
        BLENDER_THUMBNLR  = BLENDER_THUMBNLR if config["blender_thumbnailer_path"] == "" else config["blender_thumbnailer_path"]
        HIDE_HIDDEN_FILES = True  if config["hide_hidden_files"] in ["true", ""] else False
        go_past_home      = True  if config["go_past_home"] in ["true", ""] else False
        lock_folder       = False if config["lock_folder"] in ["false", ""] else True
        locked_folders    = config["locked_folders"].split("::::")
        mplayer_options   = config["mplayer_options"].split()
        music_app         = config["music_app"]
        media_app         = config["media_app"]
        image_app         = config["image_app"]
        office_app        = config["office_app"]
        pdf_app           = config["pdf_app"]
        code_app          = config["code_app"]
        text_app          = config["text_app"]
        terminal_app      = config["terminal_app"]
        container_icon_wh = config["container_icon_wh"]
        video_icon_wh     = config["video_icon_wh"]
        sys_icon_wh       = config["sys_icon_wh"]
        file_manager_app  = config["file_manager_app"]
        remux_folder_max_disk_usage = config["remux_folder_max_disk_usage"]

        # Filters
        filters = settings["filters"]
        fmeshs  = tuple(filters["meshs"])
        fcode   = tuple(filters["code"])
        fvideos = tuple(filters["videos"])
        foffice = tuple(filters["office"])
        fimages = tuple(filters["images"])
        ftext   = tuple(filters["text"])
        fmusic  = tuple(filters["music"])
        fpdf    = tuple(filters["pdf"])
