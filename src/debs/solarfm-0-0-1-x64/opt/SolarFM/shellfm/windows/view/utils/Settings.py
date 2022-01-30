# System import
import json
import os
from os import path

# Lib imports


# Apoplication imports



class Settings:
    logger            = None

    USR_SOLARFM       = "/usr/share/solarfm"
    USER_HOME         = path.expanduser('~')
    CONFIG_PATH       = f"{USER_HOME}/.config/solarfm"
    CONFIG_FILE       = f"{CONFIG_PATH}/settings.json"
    HIDE_HIDDEN_FILES = True

    GTK_ORIENTATION   = 1      # HORIZONTAL (0) VERTICAL (1)
    DEFAULT_ICONS     = f"{CONFIG_PATH}/icons"
    DEFAULT_ICON      = f"{DEFAULT_ICONS}/text.png"
    FFMPG_THUMBNLR    = f"{CONFIG_PATH}/ffmpegthumbnailer" # Thumbnail generator binary
    REMUX_FOLDER      = f"{USER_HOME}/.remuxs"             # Remuxed files folder

    STEAM_BASE_URL    = "https://steamcdn-a.akamaihd.net/steam/apps/"
    ICON_DIRS         = ["/usr/share/pixmaps", "/usr/share/icons", f"{USER_HOME}/.icons" ,]
    BASE_THUMBS_PTH   = f"{USER_HOME}/.thumbnails"         # Used for thumbnail generation
    ABS_THUMBS_PTH    = f"{BASE_THUMBS_PTH}/normal"        # Used for thumbnail generation
    STEAM_ICONS_PTH   = f"{BASE_THUMBS_PTH}/steam_icons"
    CONTAINER_ICON_WH = [128, 128]
    VIDEO_ICON_WH     = [128, 64]
    SYS_ICON_WH       = [56, 56]

    # CONTAINER_ICON_WH = [128, 128]
    # VIDEO_ICON_WH     = [96, 48]
    # SYS_ICON_WH       = [96, 96]

    subpath           = ""
    go_past_home      = None
    lock_folder       = None
    locked_folders    = None
    mplayer_options   = None
    music_app         = None
    media_app         = None
    image_app         = None
    office_app        = None
    pdf_app           = None
    text_app          = None
    file_manager_app  = None
    remux_folder_max_disk_usage = None

    if path.isfile(CONFIG_FILE):
        with open(CONFIG_FILE) as infile:
            settings          = json.load(infile)["settings"]

            subpath           = settings["base_of_home"]
            HIDE_HIDDEN_FILES = True if settings["hide_hidden_files"] == "true" else False
            FFMPG_THUMBNLR    = FFMPG_THUMBNLR if settings["thumbnailer_path"] == "" else settings["thumbnailer_path"]
            go_past_home      = True if settings["go_past_home"] == "" else settings["go_past_home"] 
            lock_folder       = True if settings["lock_folder"] == "true" else False
            locked_folders    = settings["locked_folders"].split("::::")
            mplayer_options   = settings["mplayer_options"].split()
            music_app         = settings["music_app"]
            media_app         = settings["media_app"]
            image_app         = settings["image_app"]
            office_app        = settings["office_app"]
            pdf_app           = settings["pdf_app"]
            text_app          = settings["text_app"]
            file_manager_app  = settings["file_manager_app"]
            terminal_app      = settings["terminal_app"]
            remux_folder_max_disk_usage = settings["remux_folder_max_disk_usage"]

    # Filters
    fvideos = ('.mkv', '.avi', '.flv', '.mov', '.m4v', '.mpg', '.wmv', '.mpeg', '.mp4', '.webm')
    foffice = ('.doc', '.docx', '.xls', '.xlsx', '.xlt', '.xltx', '.xlm', '.ppt', 'pptx', '.pps', '.ppsx', '.odt', '.rtf')
    fimages = ('.png', '.jpg', '.jpeg', '.gif', '.ico', '.tga')
    ftext   = ('.txt', '.text', '.sh', '.cfg', '.conf')
    fmusic  = ('.psf', '.mp3', '.ogg', '.flac', '.m4a')
    fpdf    = ('.pdf')


    # Dir structure check
    if not path.isdir(REMUX_FOLDER):
        os.mkdir(REMUX_FOLDER)

    if not path.isdir(BASE_THUMBS_PTH):
        os.mkdir(BASE_THUMBS_PTH)

    if not path.isdir(ABS_THUMBS_PTH):
        os.mkdir(ABS_THUMBS_PTH)

    if not path.isdir(STEAM_ICONS_PTH):
        os.mkdir(STEAM_ICONS_PTH)

    if not os.path.exists(DEFAULT_ICONS):
        DEFAULT_ICONS = f"{USR_SOLARFM}/icons"
        DEFAULT_ICON  = f"{DEFAULT_ICONS}/text.png"
