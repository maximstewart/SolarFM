# Python imports
import subprocess

# Lib imports

# Application imports




class MeshsIconMixin:
    def generate_blender_thumbnail(self, full_path, hash_img_path):
        try:
            proc = subprocess.Popen([self.BLENDER_THUMBNLR, full_path, hash_img_path])
            proc.wait()
        except Exception as e:
            self.logger.debug(repr(e))
