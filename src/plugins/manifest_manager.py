# Python imports
import os
import json
from os.path import join

# Lib imports

# Application imports
from .dto.manifest_meta import ManifestMeta
from .dto.manifest import Manifest



class ManifestMapperException(Exception):
    ...



class ManifestManager:
    def __init__(self):

        self._plugins_path         = settings_manager.get_plugins_path()

        self.pre_launch_manifests  = []
        self.post_launch_manifests = []

        self.load_manifests()


    def load_manifests(self):
        logger.info(f"Loading manifests...")

        for path, folder in [
            [join(self._plugins_path, item), item]
            if
                os.path.isdir( join(self._plugins_path, item) )
            else
                None
            for item in os.listdir(self._plugins_path)
        ]:
            self.load(folder, path)

    def load(self, folder, path):
        manifest_pth = join(path, "manifest.json")

        if not os.path.exists(manifest_pth):
            raise ManifestMapperException("Invalid Plugin Structure: Plugin doesn't have 'manifest.json'. Aboarting load...")

        with open(manifest_pth) as f:
            data                   = json.load(f)
            manifest               = Manifest(**data)
            manifest_meta          = ManifestMeta()

            manifest_meta.folder   = folder
            manifest_meta.path     = path
            manifest_meta.manifest = manifest

            if manifest.pre_launch:
                self.pre_launch_manifests.append(manifest_meta)
            else:
                self.post_launch_manifests.append(manifest_meta)

    def get_pre_launch_manifests(self) -> dict:
        return self.pre_launch_manifests

    def get_post_launch_plugins(self) -> None:
        return self.post_launch_manifests

