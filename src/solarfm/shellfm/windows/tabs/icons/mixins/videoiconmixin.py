# Python imports
import subprocess

# Lib imports

# Application imports




class VideoIconMixin:
    def generate_video_thumbnail(self, full_path, hash_img_path, scrub_percent = "65%"):
        try:
            proc = subprocess.Popen([self.FFMPG_THUMBNLR, "-t", scrub_percent, "-s", "300", "-c", "jpg", "-i", full_path, "-o", hash_img_path])
            proc.wait()
        except Exception as e:
            self.logger.debug(repr(e))
            self.ffprobe_generate_video_thumbnail(full_path, hash_img_path)


    def ffprobe_generate_video_thumbnail(self, full_path, hash_img_path):
        proc = None
        try:
            # Stream duration
            command  = ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=duration", "-of", "default=noprint_wrappers=1:nokey=1", full_path]
            data     = subprocess.run(command, stdout=subprocess.PIPE)
            duration = data.stdout.decode('utf-8')

            # Format (container) duration
            if "N/A" in duration:
                command  = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", full_path]
                data     = subprocess.run(command , stdout=subprocess.PIPE)
                duration = data.stdout.decode('utf-8')

            # Stream duration type: image2
            if "N/A" in duration:
                command  = ["ffprobe", "-v", "error", "-select_streams", "v:0", "-f", "image2", "-show_entries", "stream=duration", "-of", "default=noprint_wrappers=1:nokey=1", full_path]
                data     = subprocess.run(command, stdout=subprocess.PIPE)
                duration = data.stdout.decode('utf-8')

            # Format (container) duration type: image2
            if "N/A" in duration:
                command  = ["ffprobe", "-v", "error", "-f", "image2", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", full_path]
                data     = subprocess.run(command , stdout=subprocess.PIPE)
                duration = data.stdout.decode('utf-8')

            # Get frame roughly 35% through video
            grabTime = str( int( float( duration.split(".")[0] ) * 0.35) )
            command  = ["ffmpeg", "-ss", grabTime, "-an", "-i", full_path, "-s", "320x180", "-vframes", "1", hash_img_path]
            proc     = subprocess.Popen(command, stdout=subprocess.PIPE)
            proc.wait()
        except Exception as e:
            print("Video thumbnail generation issue in thread:")
            print( repr(e) )
            self.logger.debug(repr(e))
