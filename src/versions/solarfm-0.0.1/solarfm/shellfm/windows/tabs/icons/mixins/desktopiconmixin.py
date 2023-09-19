# Python imports
import os
from os.path import isfile
import subprocess
import hashlib

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gio

# Application imports
from .xdg.DesktopEntry import DesktopEntry




class DesktopIconMixin:
    def find_thumbnail_from_desktop_file(self, full_path):
        try:
            xdgObj        = DesktopEntry(full_path)
            icon          = xdgObj.getIcon()
            alt_icon_path = ""

            if "steam" in icon:
                return self.get_steam_img(xdgObj)
            elif os.path.exists(icon):
                return self.create_scaled_image(icon, self.sys_icon_wh)
            else:
                pixbuf, alt_icon_path = self.get_icon_from_traversal(icon)
                if pixbuf:
                    return pixbuf

                return self.create_scaled_image(alt_icon_path, self.sys_icon_wh)
        except Exception as e:
            print(".desktop icon generation issue:")
            print( repr(e) )

        return None


    def get_steam_img(self, xdgObj):
        name         = xdgObj.getName()
        file_hash    = hashlib.sha256(str.encode(name)).hexdigest()
        hash_img_pth = f"{self.STEAM_ICONS_PTH}/{file_hash}.jpg"

        if not isfile(hash_img_pth):
            exec_str  = xdgObj.getExec()
            parts     = exec_str.split("steam://rungameid/")
            id        = parts[len(parts) - 1]
            imageLink = f"{self.STEAM_CDN_URL}{id}/header.jpg"
            proc      = subprocess.Popen(["wget", "-O", hash_img_pth, imageLink])
            proc.wait()

        return self.create_scaled_image(hash_img_pth, self.video_icon_wh)

    def get_icon_from_traversal(self, icon):
        gio_icon = Gio.Icon.new_for_string(icon)
        gicon    = Gtk.Image.new_from_gicon(gio_icon, 32)
        pixbuf   = gicon.get_pixbuf()

        alt_icon_path = ""
        for dir in self.ICON_DIRS:
            alt_icon_path = self.traverse_icons_folder(dir, icon)
            if alt_icon_path != "":
                break

        return pixbuf, alt_icon_path

    def traverse_icons_folder(self, path, icon):
        for (dirpath, dirnames, filenames) in os.walk(path):
            for file in filenames:
                appNM = "application-x-" + icon
                if icon in file or appNM in file:
                    return f"{dirpath}/{file}"
