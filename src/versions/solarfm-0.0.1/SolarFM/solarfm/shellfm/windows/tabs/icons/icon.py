# Python Imports
import os, subprocess, threading, hashlib
from os.path import isfile

# Lib imports
import gi
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import GdkPixbuf, GLib


try:
    from PIL import Image as PImage
except Exception as e:
    PImage = None


# Application imports
from .mixins.desktopiconmixin import DesktopIconMixin
from .mixins.videoiconmixin import VideoIconMixin


def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()
    return wrapper


class Icon(DesktopIconMixin, VideoIconMixin):
    def create_icon(self, dir, file):
        full_path = f"{dir}/{file}"
        return self.get_icon_image(dir, file, full_path)

    def get_icon_image(self, dir, file, full_path):
        try:
            thumbnl = None

            if file.lower().endswith(self.fvideos):              # Video icon
                thumbnl = self.create_thumbnail(dir, file)
            elif file.lower().endswith(self.fimages):            # Image Icon
                thumbnl = self.create_scaled_image(full_path)
            elif full_path.lower().endswith( ('.desktop',) ):    # .desktop file parsing
                thumbnl = self.parse_desktop_files(full_path)

            return thumbnl
        except Exception as e:
            return None

    def create_thumbnail(self, dir, file, scrub_percent = "65%"):
        full_path = f"{dir}/{file}"
        try:
            file_hash    = hashlib.sha256(str.encode(full_path)).hexdigest()
            hash_img_pth = f"{self.ABS_THUMBS_PTH}/{file_hash}.jpg"
            if isfile(hash_img_pth) == False:
                self.generate_video_thumbnail(full_path, hash_img_pth, scrub_percent)

            thumbnl = self.create_scaled_image(hash_img_pth, self.video_icon_wh)
            if thumbnl == None: # If no icon whatsoever, return internal default
                thumbnl = GdkPixbuf.Pixbuf.new_from_file(f"{self.DEFAULT_ICONS}/video.png")

            return thumbnl
        except Exception as e:
            print("Thumbnail generation issue:")
            print( repr(e) )
            return GdkPixbuf.Pixbuf.new_from_file(f"{self.DEFAULT_ICONS}/video.png")


    def create_scaled_image(self, path, wxh = None):
        if not wxh:
            wxh = self.video_icon_wh

        try:
            if path.lower().endswith(".gif"):
                return  GdkPixbuf.PixbufAnimation.new_from_file(path) \
                                                    .get_static_image() \
                                                    .scale_simple(wxh[0], wxh[1], GdkPixbuf.InterpType.BILINEAR)
            else:
                if PImage and path.lower().endswith(".webp"):
                    return self.image2pixbuf(path, wxh)
                else:
                    return GdkPixbuf.Pixbuf.new_from_file_at_scale(path, wxh[0], wxh[1], True)
        except Exception as e:
            print("Image Scaling Issue:")
            print( repr(e) )
            return None

    def image2pixbuf(self, path, wxh):
        """Convert Pillow image to GdkPixbuf"""
        im   = PImage.open(path)
        data = im.tobytes()
        data = GLib.Bytes.new(data)
        w, h = im.size

        pixbuf = GdkPixbuf.Pixbuf.new_from_bytes(data, GdkPixbuf.Colorspace.RGB,
                                                            False, 8, w, h, w * 3)

        return pixbuf.scale_simple(wxh[0], wxh[1], 2) # BILINEAR = 2

    def create_from_file(self, path):
        try:
            return GdkPixbuf.Pixbuf.new_from_file(path)
        except Exception as e:
            print("Image from file Issue:")
            print( repr(e) )
            return None

    def return_generic_icon(self):
        return GdkPixbuf.Pixbuf.new_from_file(self.DEFAULT_ICON)
