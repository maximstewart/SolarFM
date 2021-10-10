# System import
import os, subprocess, threading


# Lib imports


# Apoplication imports


class Launcher:
    def open_file_locally(self, file):
        lowerName = file.lower()
        command   = []

        if lowerName.endswith(self.fvideos):
            command = [self.media_app]

            if "mplayer" in self.media_app:
                command += self.mplayer_options

            command += [file]
        elif lowerName.endswith(self.fimages):
            command = [self.image_app, file]
        elif lowerName.endswith(self.fmusic):
            command = [self.music_app, file]
        elif lowerName.endswith(self.foffice):
            command = [self.office_app, file]
        elif lowerName.endswith(self.ftext):
            command = [self.text_app, file]
        elif lowerName.endswith(self.fpdf):
            command = [self.pdf_app, file]
        else:
            command = [self.file_manager_app, file]

            self.logger.debug(command)
        DEVNULL = open(os.devnull, 'w')
        subprocess.Popen(command, start_new_session=True, stdout=DEVNULL, stderr=DEVNULL, close_fds=True)


    def remux_video(self, hash, file):
        remux_vid_pth = self.REMUX_FOLDER + "/" + hash + ".mp4"
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
            except Exception as e:
                self.logger.debug(message)
                self.logger.debug(e)
                return False

        return True

    def check_remux_space(self):
        limit = self.remux_folder_max_disk_usage
        try:
            limit = int(limit)
        except Exception as e:
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
