# Python Imports
import os, subprocess, hashlib
from os.path import isfile

# Gtk imports
import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gio
from gi.repository import Gtk

# Application imports
from .xdg.DesktopEntry import DesktopEntry


class DesktopIconMixin:
    def get_system_thumbnail(self, filename, size):
        try:
            if os.path.exists(filename):
                gioFile   = Gio.File.new_for_path(filename)
                info      = gioFile.query_info('standard::icon' , 0, Gio.Cancellable())
                icon      = info.get_icon().get_names()[0]
                iconTheme = Gtk.IconTheme.get_default()
                iconData  = iconTheme.lookup_icon(icon , size , 0)
                if iconData:
                    iconPath  = iconData.get_filename()
                    return Gtk.Image.new_from_file(iconPath)
                else:
                    return None
            else:
                return None
        except Exception as e:
            print("system icon generation issue:")
            print( repr(e) )
            return None

    def parse_desktop_files(self, full_path):
        try:
            xdgObj        = DesktopEntry(full_path)
            icon          = xdgObj.getIcon()
            alt_icon_path = ""

            if "steam" in icon:
                name         = xdgObj.getName()
                file_hash    = hashlib.sha256(str.encode(name)).hexdigest()
                hash_img_pth = self.STEAM_ICONS_PTH + "/" + file_hash + ".jpg"

                if isfile(hash_img_pth) == True:
                    # Use video sizes since headers are bigger
                    return self.create_scaled_image(hash_img_pth, self.VIDEO_ICON_WH)

                exec_str  = xdgObj.getExec()
                parts     = exec_str.split("steam://rungameid/")
                id        = parts[len(parts) - 1]
                imageLink = self.STEAM_BASE_URL + id + "/header.jpg"
                proc      = subprocess.Popen(["wget", "-O", hash_img_pth, imageLink])
                proc.wait()

                # Use video thumbnail sizes since headers are bigger
                return self.create_scaled_image(hash_img_pth, self.VIDEO_ICON_WH)
            elif os.path.exists(icon):
                return self.create_scaled_image(icon, self.SYS_ICON_WH)
            else:
                alt_icon_path = ""

                for dir in self.ICON_DIRS:
                    alt_icon_path = self.traverse_icons_folder(dir, icon)
                    if alt_icon_path != "":
                        break

                return self.create_scaled_image(alt_icon_path, self.SYS_ICON_WH)
        except Exception as e:
            print(".desktop icon generation issue:")
            print( repr(e) )
            return None

    def traverse_icons_folder(self, path, icon):
        alt_icon_path = ""

        for (dirpath, dirnames, filenames) in os.walk(path):
            for file in filenames:
                appNM = "application-x-" + icon
                if icon in file or appNM in file:
                    alt_icon_path = dirpath + "/" + file
                    break

        return alt_icon_path
