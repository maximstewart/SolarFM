# Python imports
import hashlib
from os.path import isfile

# Lib imports
import gi
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import GLib
from gi.repository import Gio
from gi.repository import GdkPixbuf

try:
    from PIL import Image as PImage
except Exception as e:
    PImage = None

# Application imports
from .mixins.videoiconmixin import VideoIconMixin
from .mixins.meshsiconmixin import MeshsIconMixin
from .mixins.desktopiconmixin import DesktopIconMixin




class Icon(DesktopIconMixin, VideoIconMixin, MeshsIconMixin):
    def create_icon(self, dir, file):
        full_path = f"{dir}/{file}"
        return self.get_icon_image(dir, file, full_path)

    def get_icon_image(self, dir, file, full_path):
        try:
            thumbnl = None

            if file.lower().endswith(self.fmeshs):               # 3D Mesh icon
                ...
            if file.lower().endswith(self.fvideos):              # Video icon
                thumbnl = self.create_thumbnail(dir, file, full_path)
            elif file.lower().endswith(self.fimages):            # Image Icon
                thumbnl = self.create_scaled_image(full_path)
            elif file.lower().endswith( (".blend",) ):           # Blender icon
                thumbnl = self.create_blender_thumbnail(dir, file, full_path)
            elif full_path.lower().endswith( ('.desktop',) ):    # .desktop file parsing
                thumbnl = self.parse_desktop_files(full_path)

            if not thumbnl:
                thumbnl = self.get_system_thumbnail(full_path, self.sys_icon_wh[0])

            if not thumbnl:
                thumbnl = self.return_generic_icon()

            return thumbnl
        except Exception:
            ...

        return self.return_generic_icon()

    def create_blender_thumbnail(self, dir, file, full_path=None):
        try:
            file_hash     = hashlib.sha256(str.encode(full_path)).hexdigest()
            hash_img_path = f"{self.ABS_THUMBS_PTH}/{file_hash}.png"
            if not isfile(hash_img_path):
                self.generate_blender_thumbnail(full_path, hash_img_path)

            return self.create_scaled_image(hash_img_path, self.video_icon_wh)
        except Exception as e:
            print("Blender thumbnail generation issue:")
            print( repr(e) )

        return None

    def create_thumbnail(self, dir, file, full_path=None, scrub_percent = "65%"):
        try:
            file_hash     = hashlib.sha256(str.encode(full_path)).hexdigest()
            hash_img_path = f"{self.ABS_THUMBS_PTH}/{file_hash}.jpg"
            if not isfile(hash_img_path):
                self.generate_video_thumbnail(full_path, hash_img_path, scrub_percent)

            return self.create_scaled_image(hash_img_path, self.video_icon_wh)
        except Exception as e:
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
            except Exception as e:
                print("Image Scaling Issue:")
                print( repr(e) )

        return None

    def image2pixbuf(self, full_path, wxh):
        """Convert Pillow image to GdkPixbuf"""
        im   = PImage.open(full_path)
        data = im.tobytes()
        data = GLib.Bytes.new(data)
        w, h = im.size

        pixbuf = GdkPixbuf.Pixbuf.new_from_bytes(data, GdkPixbuf.Colorspace.RGB,
                                                            False, 8, w, h, w * 3)

        return pixbuf.scale_simple(wxh[0], wxh[1], 2) # BILINEAR = 2

    def create_from_file(self, full_path):
        try:
            return GdkPixbuf.Pixbuf.new_from_file(full_path)
        except Exception as e:
            print("Image from file Issue:")
            print( repr(e) )

        return None

    def get_system_thumbnail(self, filename, size):
        try:
            gio_file  = Gio.File.new_for_path(filename)
            info      = gio_file.query_info('standard::icon' , 0, None)
            icon      = info.get_icon().get_names()[0]
            icon_path = settings.get_icon_theme().lookup_icon(icon , size , 0).get_filename()

            return GdkPixbuf.Pixbuf.new_from_file(icon_path)
        except Exception:
            ...

        return None

    def return_generic_icon(self):
        return GdkPixbuf.Pixbuf.new_from_file(self.DEFAULT_ICON)
