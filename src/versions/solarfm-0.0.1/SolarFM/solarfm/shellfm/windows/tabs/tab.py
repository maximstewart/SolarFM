# Python imports
import hashlib
import re
from os import listdir
from os.path import isdir
from os.path import isfile
from os.path import join
from random import randint

# Lib imports

# Application imports
from .utils.settings import Settings
from .utils.launcher import Launcher
from .utils.filehandler import FileHandler
from .icons.icon import Icon
from .path import Path




class Tab(Settings, FileHandler, Launcher, Icon, Path):
    def __init__(self):
        self.logger             = None
        self._id_length: int    = 10

        self._id: str           = ""
        self._wid: str          = None
        self._dir_watcher       = None
        self._hide_hidden: bool = self.HIDE_HIDDEN_FILES
        self._files: list       = []
        self._dirs: list        = []
        self._vids: list        = []
        self._images: list      = []
        self._desktop: list     = []
        self._ungrouped: list   = []
        self._hidden: list      = []

        self._generate_id()
        self.set_to_home()

    def load_directory(self) -> None:
        path            = self.get_path()
        self._dirs      = []
        self._vids      = []
        self._images    = []
        self._desktop   = []
        self._ungrouped = []
        self._hidden    = []
        self._files     = []

        if not isdir(path):
            self.set_to_home()
            return ""

        for f in listdir(path):
            file = join(path, f)
            if self._hide_hidden:
                if f.startswith('.'):
                    self._hidden.append(f)
                    continue

            if isfile(file):
                lowerName = file.lower()
                if lowerName.endswith(self.fvideos):
                    self._vids.append(f)
                elif lowerName.endswith(self.fimages):
                    self._images.append(f)
                elif lowerName.endswith((".desktop",)):
                    self._desktop.append(f)
                else:
                    self._ungrouped.append(f)
            else:
                self._dirs.append(f)

        self._dirs.sort(key=self._natural_keys)
        self._vids.sort(key=self._natural_keys)
        self._images.sort(key=self._natural_keys)
        self._desktop.sort(key=self._natural_keys)
        self._ungrouped.sort(key=self._natural_keys)

        self._files = self._dirs + self._vids + self._images + self._desktop + self._ungrouped

    def is_folder_locked(self, hash):
        if self.lock_folder:
            path_parts = self.get_path().split('/')
            file       = self.get_path_part_from_hash(hash)

            # Insure chilren folders are locked too.
            lockedFolderInPath = False
            for folder in self.locked_folders:
                if folder in path_parts:
                    lockedFolderInPath = True
                    break

            return (file in self.locked_folders or lockedFolderInPath)
        else:
            return False


    def get_not_hidden_count(self) -> int:
        return len(self._files)    + \
                len(self._dirs)    + \
                len(self._vids)    + \
                len(self._images)  + \
                len(self._desktop) + \
                len(self._ungrouped)

    def get_hidden_count(self) -> int:
        return len(self._hidden)

    def get_files_count(self) -> int:
        return len(self._files)

    def get_path_part_from_hash(self, hash: str) -> str:
        files = self.get_files()
        file  = None

        for f in files:
            if hash == f[1]:
                file = f[0]
                break

        return file

    def get_files_formatted(self) -> dict:
        files     = self._hash_set(self._files),
        dirs      = self._hash_set(self._dirs),
        videos    = self.get_videos(),
        images    = self._hash_set(self._images),
        desktops  = self._hash_set(self._desktop),
        ungrouped = self._hash_set(self._ungrouped)
        hidden    = self._hash_set(self._hidden)

        return {
            'path_head': self.get_path(),
            'list': {
                'files': files,
                'dirs': dirs,
                'videos': videos,
                'images': images,
                'desktops': desktops,
                'ungrouped': ungrouped,
                'hidden': hidden
            }
        }

    def get_pixbuf_icon_str_combo(self):
        data = []
        dir  = self.get_current_directory()
        for file in self._files:
            icon = self.create_icon(dir, file).get_pixbuf()
            data.append([icon, file])

        return data


    def get_gtk_icon_str_combo(self) -> list:
        data = []
        dir  = self.get_current_directory()
        for file in self._files:
            icon = self.create_icon(dir, file)
            data.append([icon, file[0]])

        return data

    def get_current_directory(self) -> str:
        return self.get_path()

    def get_current_sub_path(self) -> str:
        path = self.get_path()
        home = f"{self.get_home()}/"
        return path.replace(home, "")

    def get_end_of_path(self) -> str:
        parts = self.get_current_directory().split("/")
        size  = len(parts)
        return parts[size - 1]


    def set_hiding_hidden(self, state: bool) -> None:
        self._hide_hidden = state

    def is_hiding_hidden(self) -> bool:
        return self._hide_hidden

    def get_dot_dots(self) -> list:
        return self._hash_set(['.', '..'])

    def get_files(self) -> list:
        return self._hash_set(self._files)

    def get_dirs(self) -> list:
        return self._hash_set(self._dirs)

    def get_videos(self) -> list:
        return self._hash_set(self._vids)

    def get_images(self) -> list:
        return self._hash_set(self._images)

    def get_desktops(self) -> list:
        return self._hash_set(self._desktop)

    def get_ungrouped(self) -> list:
        return self._hash_set(self._ungrouped)

    def get_hidden(self) -> list:
        return self._hash_set(self._hidden)

    def get_id(self) -> str:
        return self._id

    def set_wid(self, _wid: str) -> None:
        self._wid = _wid

    def get_wid(self) -> str:
        return self._wid

    def set_dir_watcher(self, watcher):
        self._dir_watcher = watcher

    def get_dir_watcher(self):
        return self._dir_watcher

    def _atoi(self, text):
        return int(text) if text.isdigit() else text

    def _natural_keys(self, text):
        return [ self._atoi(c) for c in re.split('(\d+)',text) ]

    def _hash_text(self, text) -> str:
        return hashlib.sha256(str.encode(text)).hexdigest()[:18]

    def _hash_set(self, arry: list) -> list:
        data = []
        for arr in arry:
            data.append([arr, self._hash_text(arr)])
        return data

    def _random_with_N_digits(self, n: int) -> int:
        range_start = 10**(n-1)
        range_end = (10**n)-1
        return randint(range_start, range_end)

    def _generate_id(self) -> str:
        self._id = str(self._random_with_N_digits(self._id_length))
