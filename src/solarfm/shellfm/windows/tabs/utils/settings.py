# Python imports
import json
import os
from os import path

# Lib imports

# Apoplication imports


class ShellFMSettingsException(Exception):
    ...



class Settings:
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

    REMUX_FOLDER      = f"{USER_HOME}/.remuxs"                # Remuxed files folder

    with open(CONFIG_FILE) as f:
        settings          = json.load(f)
        config            = settings["config"]

        subpath           = config["base_of_home"]
        HIDE_HIDDEN_FILES = True  if config["hide_hidden_files"] in ["true", ""] else False
        go_past_home      = True  if config["go_past_home"] in ["true", ""] else False
        lock_folder       = False if config["lock_folder"] in ["false", ""] else True
        locked_folders    = config["locked_folders"].split("::::")
        mplayer_options   = config["mplayer_options"].split()
        use_defined_launchers = config["use_defined_launchers"]
        music_app         = config["music_app"]
        media_app         = config["media_app"]
        image_app         = config["image_app"]
        office_app        = config["office_app"]
        pdf_app           = config["pdf_app"]
        code_app          = config["code_app"]
        text_app          = config["text_app"]
        terminal_app      = config["terminal_app"]
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
