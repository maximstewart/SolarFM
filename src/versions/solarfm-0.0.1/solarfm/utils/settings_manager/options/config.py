# Python imports
from dataclasses import dataclass

# Lib imports

# Application imports


@dataclass
class Config:
    base_of_home: str
    hide_hidden_files: str
    thumbnailer_path: str
    blender_thumbnailer_path: str
    go_past_home: str
    lock_folder: str
    locked_folders: str
    mplayer_options: str
    music_app: str
    media_app: str
    image_app: str
    office_app: str
    pdf_app: str
    code_app: str
    text_app: str
    terminal_app: str
    container_icon_wh: []
    video_icon_wh: []
    sys_icon_wh: []
    file_manager_app: str
    steam_cdn_url: str
    remux_folder_max_disk_usage: str
