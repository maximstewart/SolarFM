
# Gtk Imports
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')

from gi.repository import Gtk as gtk
from gi.repository import Gio as gio
from gi.repository import GdkPixbuf
from xdg.DesktopEntry import DesktopEntry

# Python Imports
import os, subprocess, hashlib, threading

from os.path import isdir, isfile, join



def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()
    return wrapper

class Icon:
    def __init__(self, settings):
        self.settings          = settings
        self.thubnailGen       = settings.getThumbnailGenerator()
        self.vidsList          = settings.returnVidsExtensionList()
        self.imagesList        = settings.returnImagesExtensionList()
        self.GTK_ORIENTATION   = settings.returnIconImagePos()
        self.usrHome           = settings.returnUserHome()
        self.iconContainerWH   = settings.returnContainerWH()
        self.systemIconImageWH = settings.returnSystemIconImageWH()
        self.viIconWH          = settings.returnVIIconWH()


    def createIcon(self, dir, file):
        fullPath = dir + "/" + file
        return self.getIconImage(file, fullPath)


    def getIconImage(self, file, fullPath):
        try:
            thumbnl    = None

            # Video thumbnail
            if file.lower().endswith(self.vidsList):
                fileHash   = hashlib.sha256(str.encode(fullPath)).hexdigest()
                hashImgPth = self.usrHome + "/.thumbnails/normal/" + fileHash + ".png"

                if isfile(hashImgPth) == False:
                    self.generateVideoThumbnail(fullPath, hashImgPth)

                thumbnl  = self.createIconImageBuffer(hashImgPth, self.viIconWH)
            # Image Icon
            elif file.lower().endswith(self.imagesList):
                thumbnl  = self.createIconImageBuffer(fullPath, self.viIconWH)
            # .desktop file parsing
            elif fullPath.lower().endswith( ('.desktop',) ):
                thumbnl  = self.parseDesktopFiles(fullPath)
            # System icons
            else:
                thumbnl  = self.getSystemThumbnail(fullPath, self.systemIconImageWH[0])

            if thumbnl == None: # If no icon, try stock file icon...
                thumbnl  = gtk.Image.new_from_icon_name("gtk-file", gtk.IconSize.LARGE_TOOLBAR)

            if thumbnl == None: # If no icon whatsoever, return internal default
                thumbnl  = gtk.Image.new_from_file("resources/icons/bin.png")

            return thumbnl
        except Exception as e:
            print(e)
            return gtk.Image.new_from_file("resources/icons/bin.png")


    def parseDesktopFiles(self, fullPath):
        try:
            xdgObj      = DesktopEntry(fullPath)
            icon        = xdgObj.getIcon()
            iconsDirs   = "/usr/share/icons"
            altIconPath = ""

            if "steam" in icon:
                steamIconsDir = self.usrHome + "/.thumbnails/steam_icons/"
                name          = xdgObj.getName()
                fileHash      = hashlib.sha256(str.encode(name)).hexdigest()

                if isdir(steamIconsDir) == False:
                    os.mkdir(steamIconsDir)

                hashImgPth = steamIconsDir + fileHash + ".jpg"
                if isfile(hashImgPth) == True:
                    # Use video sizes since headers are bigger
                    return self.createIconImageBuffer(hashImgPth, self.viIconWH)

                execStr   = xdgObj.getExec()
                parts     = execStr.split("steam://rungameid/")
                id        = parts[len(parts) - 1]

                # NOTE: Can try this logic instead...
                # if command exists use it instead of header image
                # if "steamcmd app_info_print id":
                #     proc = subprocess.Popen(["steamcmd", "app_info_print", id])
                #     proc.wait()
                # else:
                #     use the bottom logic

                imageLink = "https://steamcdn-a.akamaihd.net/steam/apps/" + id + "/header.jpg"
                proc      = subprocess.Popen(["wget", "-O", hashImgPth, imageLink])
                proc.wait()

                # Use video sizes since headers are bigger
                return self.createIconImageBuffer(hashImgPth, self.viIconWH)
            elif os.path.exists(icon):
                return self.createIconImageBuffer(icon, self.systemIconImageWH)
            else:
                for (dirpath, dirnames, filenames) in os.walk(iconsDirs):
                    for file in filenames:
                        appNM = "application-x-" + icon
                        if appNM in file:
                            altIconPath = dirpath + "/" + file
                            break

                return self.createIconImageBuffer(altIconPath, self.systemIconImageWH)
        except Exception as e:
            print(e)
            return None


    def getSystemThumbnail(self, filename, size):
        try:
            iconPath = None
            if os.path.exists(filename):
                file      = gio.File.new_for_path(filename)
                info      = file.query_info('standard::icon' , 0 , gio.Cancellable())
                icon      = info.get_icon().get_names()[0]
                iconTheme = gtk.IconTheme.get_default()
                iconFile  = iconTheme.lookup_icon(icon , size , 0)

                if iconFile != None:
                    iconPath = iconFile.get_filename()
                    return self.createIconImageBuffer(iconPath, self.systemIconImageWH)
                else:
                    return None
            else:
                return None
        except Exception as e:
            print(e)
            return None


    def createIconImageBuffer(self, path, wxh):
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(path, wxh[0], wxh[1], False)
        except Exception as e:
            return None

        return gtk.Image.new_from_pixbuf(pixbuf)


    def generateVideoThumbnail(self, fullPath, hashImgPth):
        try:
            proc = subprocess.Popen([self.thubnailGen, "-t", "65%", "-s", "300", "-c", "jpg", "-i", fullPath, "-o", hashImgPth])
            proc.wait()
        except Exception as e:
            print(e)
