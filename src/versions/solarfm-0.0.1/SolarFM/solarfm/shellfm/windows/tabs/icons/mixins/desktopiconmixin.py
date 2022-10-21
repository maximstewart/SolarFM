# Python Imports
import os, subprocess, hashlib
from os.path import isfile

# Gtk imports

# Application imports
from .xdg.DesktopEntry import DesktopEntry


class DesktopIconMixin:
    def parse_desktop_files(self, full_path):
        try:
            xdgObj        = DesktopEntry(full_path)
            icon          = xdgObj.getIcon()
            alt_icon_path = ""

            if "steam" in icon:
                name         = xdgObj.getName()
                file_hash    = hashlib.sha256(str.encode(name)).hexdigest()
                hash_img_pth = f"{self.STEAM_ICONS_PTH}/{file_hash}.jpg"

                if isfile(hash_img_pth) == True:
                    # Use video sizes since headers are bigger
                    return self.create_scaled_image(hash_img_pth, self.video_icon_wh)

                exec_str  = xdgObj.getExec()
                parts     = exec_str.split("steam://rungameid/")
                id        = parts[len(parts) - 1]
                imageLink = f"{self.STEAM_CDN_URL}{id}/header.jpg"
                proc      = subprocess.Popen(["wget", "-O", hash_img_pth, imageLink])
                proc.wait()

                # Use video thumbnail sizes since headers are bigger
                return self.create_scaled_image(hash_img_pth, self.video_icon_wh)
            elif os.path.exists(icon):
                return self.create_scaled_image(icon, self.sys_icon_wh)
            else:
                alt_icon_path = ""

                for dir in self.ICON_DIRS:
                    alt_icon_path = self.traverse_icons_folder(dir, icon)
                    if alt_icon_path != "":
                        break

                return self.create_scaled_image(alt_icon_path, self.sys_icon_wh)
        except Exception as e:
            print(".desktop icon generation issue:")
            print( repr(e) )
            return None

    def traverse_icons_folder(self, path, icon):
        for (dirpath, dirnames, filenames) in os.walk(path):
            for file in filenames:
                appNM = "application-x-" + icon
                if icon in file or appNM in file:
                    return f"{dirpath}/{file}"
