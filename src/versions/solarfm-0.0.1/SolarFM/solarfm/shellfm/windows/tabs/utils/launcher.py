# Python imports
import os
import subprocess

# Lib imports

# Apoplication imports


class ShellFMLauncherException(Exception):
    ...



class Launcher:
    def open_file_locally(self, file):
        lowerName = file.lower()
        command   = []

        if lowerName.endswith(self.fvideos):
            command = [self.media_app, file]
        elif lowerName.endswith(self.fimages):
            command = [self.image_app, file]
        elif lowerName.endswith(self.fmusic):
            command = [self.music_app, file]
        elif lowerName.endswith(self.foffice):
            command = [self.office_app, file]
        elif lowerName.endswith(self.fcode):
            command = [self.code_app, file]
        elif lowerName.endswith(self.ftext):
            command = [self.text_app, file]
        elif lowerName.endswith(self.fpdf):
            command = [self.pdf_app, file]
        elif lowerName.endswith("placeholder-until-i-can-get-a-use-pref-fm-flag"):
            command = [self.file_manager_app, file]
        else:
            command = ["xdg-open", file]

        self.execute(command)


    def execute(self, command, start_dir=os.getenv("HOME"), use_shell=False):
        try:
            self.logger.debug(command)
            subprocess.Popen(command, cwd=start_dir, shell=use_shell, start_new_session=True, stdout=None, stderr=None, close_fds=True)
        except ShellFMLauncherException as e:
            self.logger.error(f"Couldn't execute: {command}")
            self.logger.error(e)

    # TODO: Return std(out/in/err) handlers along with subprocess instead of sinking to null
    def execute_and_return_thread_handler(self, command, start_dir=os.getenv("HOME"), use_shell=False):
        try:
            DEVNULL = open(os.devnull, 'w')
            return subprocess.Popen(command, cwd=start_dir, shell=use_shell, start_new_session=False, stdout=DEVNULL, stderr=DEVNULL, close_fds=False)
        except ShellFMLauncherException as e:
            self.logger.error(f"Couldn't execute and return thread: {command}")
            self.logger.error(e)
            return None

    @threaded
    def app_chooser_exec(self, app_info, uris):
        app_info.launch_uris_async(uris)

    def remux_video(self, hash, file):
        remux_vid_pth = "{self.REMUX_FOLDER}/{hash}.mp4"
        self.logger.debug(remux_vid_pth)

        if not os.path.isfile(remux_vid_pth):
            self.check_remux_space()

            command = ["ffmpeg", "-i", file, "-hide_banner", "-movflags", "+faststart"]
            if file.endswith("mkv"):
                command += ["-codec", "copy", "-strict", "-2"]
            if file.endswith("avi"):
                command += ["-c:v", "libx264", "-crf", "21", "-c:a", "aac", "-b:a", "192k", "-ac", "2"]
            if file.endswith("wmv"):
                command += ["-c:v", "libx264", "-crf", "23", "-c:a", "aac", "-strict", "-2", "-q:a", "100"]
            if file.endswith("f4v") or file.endswith("flv"):
                command += ["-vcodec", "copy"]

            command += [remux_vid_pth]
            try:
                proc = subprocess.Popen(command)
                proc.wait()
            except ShellFMLauncherException as e:
                self.logger.error(message)
                self.logger.error(e)
                return False

        return True

    def check_remux_space(self):
        limit = self.remux_folder_max_disk_usage
        try:
            limit = int(limit)
        except ShellFMLauncherException as e:
            self.logger.debug(e)
            return

        usage = self.get_remux_folder_usage(self.REMUX_FOLDER)
        if usage > limit:
            files = os.listdir(self.REMUX_FOLDER)
            for file in files:
                fp = os.path.join(self.REMUX_FOLDER, file)
                os.unlink(fp)


    def get_remux_folder_usage(self, start_path = "."):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(start_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if not os.path.islink(fp): # Skip if it is symbolic link
                    total_size += os.path.getsize(fp)

        return total_size
