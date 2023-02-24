# Python imports
import os
from os.path import isfile
import hashlib
import threading

# Lib imports
import gi
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import GLib
from gi.repository import Gio
from gi.repository import GdkPixbuf

try:
    from PIL import Image as PImage
except ModuleNotFoundError as e:
    PImage = None

# Application imports
from .mixins.videoiconmixin import VideoIconMixin
from .mixins.meshsiconmixin import MeshsIconMixin
from .mixins.desktopiconmixin import DesktopIconMixin



class IconException(Exception):
    ...



class Icon(DesktopIconMixin, VideoIconMixin, MeshsIconMixin):
    def create_icon(self, dir, file):
        full_path = f"{dir}/{file}"
        return self.get_icon_image(dir, file, full_path)

    def get_icon_image(self, dir, file, full_path):
        try:
            thumbnl = self._get_system_thumbnail_gtk_thread(full_path, self.sys_icon_wh[0])

            if file.lower().endswith(self.fmeshs):               # 3D Mesh icon
                ...
            if file.lower().endswith(self.fvideos):              # Video icon
                thumbnl = self.create_video_thumbnail(full_path)
            elif file.lower().endswith(self.fimages):            # Image Icon
                thumbnl = self.create_scaled_image(full_path)
            elif file.lower().endswith( (".blend",) ):           # Blender icon
                thumbnl = self.create_blender_thumbnail(full_path)
            elif full_path.lower().endswith( ('.desktop',) ):    # .desktop file parsing
                thumbnl = self.find_thumbnail_from_desktop_file(full_path)

            if not thumbnl:
                raise IconException("No known icons found.")

            return thumbnl
        except IconException:
            ...

        return self.get_generic_icon()

    def create_blender_thumbnail(self, full_path, returnHashInstead=False):
        try:
            path_exists, img_hash, hash_img_path = self.generate_hash_and_path(full_path)
            if not path_exists:
                self.generate_blender_thumbnail(full_path, hash_img_path)

            if returnHashInstead:
                return img_hash, hash_img_path

            return self.create_scaled_image(hash_img_path, self.video_icon_wh)
        except IconException as e:
            print("Blender thumbnail generation issue:")
            print( repr(e) )

        return None

    def create_video_thumbnail(self, full_path, scrub_percent = "65%", replace=False, returnHashInstead=False):
        try:
            path_exists, img_hash, hash_img_path = self.generate_hash_and_path(full_path)
            if path_exists and replace:
                os.remove(hash_img_path)
                path_exists = False

            if not path_exists:
                self.generate_video_thumbnail(full_path, hash_img_path, scrub_percent)

            if returnHashInstead:
                return img_hash, hash_img_path

            return self.create_scaled_image(hash_img_path, self.video_icon_wh)
        except IconException as e:
            print("Image/Video thumbnail generation issue:")
            print( repr(e) )

        return None


    def create_scaled_image(self, full_path, wxh = None):
        if not wxh:
            wxh = self.video_icon_wh

        if full_path:
            try:
                if full_path.lower().endswith(".gif"):
                    return  GdkPixbuf.PixbufAnimation.new_from_file(full_path) \
                                                        .get_static_image() \
                                                        .scale_simple(wxh[0], wxh[1], GdkPixbuf.InterpType.BILINEAR)
                elif full_path.lower().endswith(".webp") and PImage:
                    return self.image2pixbuf(full_path, wxh)

                return GdkPixbuf.Pixbuf.new_from_file_at_scale(full_path, wxh[0], wxh[1], True)
            except IconException as e:
                print("Image Scaling Issue:")
                print( repr(e) )

        return None

    def create_from_file(self, full_path):
        try:
            return GdkPixbuf.Pixbuf.new_from_file(full_path)
        except IconException as e:
            print("Image from file Issue:")
            print( repr(e) )

        return None

    def _get_system_thumbnail_gtk_thread(self, full_path, size):
        def _call_gtk_thread(event, result):
            result.append( self.get_system_thumbnail(full_path, size) )
            event.set()

        result  = []
        event   = threading.Event()
        GLib.idle_add(_call_gtk_thread, event, result)
        event.wait()
        return result[0]


    def get_system_thumbnail(self, full_path, size):
        try:
            gio_file  = Gio.File.new_for_path(full_path)
            info      = gio_file.query_info('standard::icon' , 0, None)
            icon      = info.get_icon().get_names()[0]
            data      = settings.get_icon_theme().lookup_icon(icon , size , 0)

            if data:
                icon_path = data.get_filename()
                return GdkPixbuf.Pixbuf.new_from_file(icon_path)

            raise IconException("No system icon found...")
        except IconException:
            ...

        return None

    def get_generic_icon(self):
        return GdkPixbuf.Pixbuf.new_from_file(self.DEFAULT_ICON)

    def generate_hash_and_path(self, full_path):
        img_hash      = self.fast_hash(full_path)
        hash_img_path = f"{self.ABS_THUMBS_PTH}/{img_hash}.jpg"
        path_exists   = True if isfile(hash_img_path) else False

        return path_exists, img_hash, hash_img_path


    def fast_hash(self, filename, hash_factory=hashlib.md5, chunk_num_blocks=128, i=1):
        h = hash_factory()
        with open(filename,'rb') as f:
            f.seek(0, 2)
            mid = int(f.tell() / 2)
            f.seek(mid, 0)

            while chunk := f.read(chunk_num_blocks*h.block_size):
                h.update(chunk)
                if (i == 12):
                    break

                i += 1

        return h.hexdigest()

    def image2pixbuf(self, full_path, wxh):
        """Convert Pillow image to GdkPixbuf"""
        im   = PImage.open(full_path)
        data = im.tobytes()
        data = GLib.Bytes.new(data)
        w, h = im.size

        pixbuf = GdkPixbuf.Pixbuf.new_from_bytes(data, GdkPixbuf.Colorspace.RGB,
                                                            False, 8, w, h, w * 3)

        return pixbuf.scale_simple(wxh[0], wxh[1], 2) # BILINEAR = 2
