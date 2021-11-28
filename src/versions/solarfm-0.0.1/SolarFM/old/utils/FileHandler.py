
import os, shutil, subprocess, threading


def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()
    return wrapper

class FileHandler:
    def __init__(self):
        # 'Filters'
        self.office = ('.doc', '.docx', '.xls', '.xlsx', '.xlt', '.xltx' '.xlm', '.ppt', 'pptx', '.pps', '.ppsx', '.odt', '.rtf')
        self.vids   = ('.mkv', '.avi', '.flv', '.mov', '.m4v', '.mpg', '.wmv', '.mpeg', '.mp4', '.webm')
        self.txt    = ('.txt', '.text', '.sh', '.cfg', '.conf')
        self.music  = ('.psf', '.mp3', '.ogg' , '.flac')
        self.images = ('.png', '.jpg', '.jpeg', '.gif')
        self.pdf    = ('.pdf')

        # Args
        self.MEDIAPLAYER  = "mpv";
        self.IMGVIEWER    = "mirage";
        self.MUSICPLAYER  = "/opt/deadbeef/bin/deadbeef";
        self.OFFICEPROG   = "libreoffice";
        self.TEXTVIEWER   = "leafpad";
        self.PDFVIEWER    = "evince";
        self.FILEMANAGER  = "spacefm";
        self.MPLAYER_WH   = " -xy 1600 -geometry 50%:50% ";
        self.MPV_WH       = " -geometry 50%:50% ";

    @threaded
    def openFile(self, file):
        print("Opening: " + file)
        if file.lower().endswith(self.vids):
            subprocess.Popen([self.MEDIAPLAYER, self.MPV_WH, file])
        elif file.lower().endswith(self.music):
            subprocess.Popen([self.MUSICPLAYER, file])
        elif file.lower().endswith(self.images):
            subprocess.Popen([self.IMGVIEWER, file])
        elif file.lower().endswith(self.txt):
            subprocess.Popen([self.TEXTVIEWER, file])
        elif file.lower().endswith(self.pdf):
            subprocess.Popen([self.PDFVIEWER, file])
        elif file.lower().endswith(self.office):
            subprocess.Popen([self.OFFICEPROG, file])
        else:
            subprocess.Popen(['xdg-open', file])


    def createFile(self, newFileName):
        pass

    def updateFile(self, oldFileName, newFileName):
        try:
            print("Renaming...")
            print(oldFileName + "  -->  " + newFileName)
            os.rename(oldFileName, newFileName)
            return 0
        except Exception as e:
            print("An error occured renaming the file:")
            print(e)
            return 1

    def deleteFile(self, toDeleteFile):
        try:
            print("Deleting...")
            print(toDeleteFile)
            if os.path.exists(toDeleteFile):
                if os.path.isfile(toDeleteFile):
                    os.remove(toDeleteFile)
                elif os.path.isdir(toDeleteFile):
                    shutil.rmtree(toDeleteFile)
                else:
                    print("An error occured deleting the file:")
                    return 1
            else:
                print("The folder/file does not exist")
                return 1
        except Exception as e:
            print("An error occured deleting the file:")
            print(e)
            return 1

        return 0

    def copyFile(self):
        pass

    def cutFile(self):
        pass

    def pasteFile(self):
        pass
