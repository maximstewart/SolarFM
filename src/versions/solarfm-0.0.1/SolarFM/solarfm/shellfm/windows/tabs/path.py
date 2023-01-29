# Python imports
import os

# Lib imports

# Application imports




class Path:
    def get_home(self) -> str:
        return os.path.expanduser("~") + self.subpath

    def get_path(self) -> str:
        return f"/{'/'.join(self.path)}" if self.path else f"/{''.join(self.path)}"

    def get_path_list(self) -> list:
        return self.path

    def push_to_path(self, dir: str):
        self.path.append(dir)
        self.load_directory()

    def pop_from_path(self) -> None:
        try:
            self.path.pop()

            if not self.go_past_home:
                if self.get_home() not in self.get_path():
                    self.set_to_home()

            self.load_directory()
        except Exception as e:
            pass

    def set_path(self, path: str) -> bool:
        if path == self.get_path():
            return False

        if os.path.isdir(path):
            self.path = list( filter(None, path.replace("\\", "/").split('/')) )
            self.load_directory()
            return True

        return False

    def set_path_with_sub_path(self, sub_path: str) -> bool:
        path = os.path.join(self.get_home(), sub_path)
        if path == self.get_path():
            return False

        if os.path.isdir(path):
            self.path = list( filter(None, path.replace("\\", "/").split('/')) )
            self.load_directory()
            return True

        return False

    def set_to_home(self) -> None:
        home = os.path.expanduser("~") + self.subpath
        path = list( filter(None, home.replace("\\", "/").split('/')) )
        self.path = path
        self.load_directory()
