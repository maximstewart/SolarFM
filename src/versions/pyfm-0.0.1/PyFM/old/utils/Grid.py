

# Gtk Imports
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')

from gi.repository import Gtk as gtk
from gi.repository import Gdk as gdk
from gi.repository import GLib as glib
from gi.repository import GdkPixbuf

# Python imports
import os, threading, time
from os.path import isdir, isfile, join
from os import listdir
from .Icon import Icon
from .FileHandler import FileHandler


def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()
    return wrapper

class Grid:
    def __init__(self, desktop, settings, newPath):
        self.desktop      = desktop
        self.settings     = settings
        self.filehandler  = FileHandler()

        self.store        =  gtk.ListStore(GdkPixbuf.Pixbuf, str)
        self.usrHome      = settings.returnUserHome()
        self.builder      = settings.returnBuilder()
        self.ColumnSize   = settings.returnColumnSize()
        self.currentPath  = ""
        self.selectedFile = ""

        self.desktop.set_model(self.store)
        self.desktop.set_pixbuf_column(0)
        self.desktop.set_text_column(1)
        self.desktop.connect("item-activated", self.iconLeftClickEventManager)
        self.desktop.connect("button_press_event", self.iconRightClickEventManager, (self.desktop,))
        self.desktop.connect("selection-changed", self.setIconSelectionArray, (self.desktop,))

        self.vidsList     =  settings.returnVidsExtensionList()
        self.imagesList   =  settings.returnImagesExtensionList()
        self.gtkLock      = False  # Thread checks for gtkLock
        self.threadLock   = False  # Gtk checks for thread lock
        self.helperThread = None   # Helper thread object
        self.toWorkPool   = []     # Thread fills pool and gtk empties it
        self.copyCutArry  = []

        self.setIconViewDir(newPath)

    def setIconViewDir(self, path):
        self.store.clear()

        self.currentPath = path
        dirPaths         = ['.', '..']
        vids             = []
        images           = []
        desktop          = []
        files            = []

        for f in listdir(path):
            file = join(path, f)
            if self.settings.isHideHiddenFiles():
                if f.startswith('.'):
                    continue
            if isfile(file):
                if file.lower().endswith(self.vidsList):
                    vids.append(f)
                elif file.lower().endswith(self.imagesList):
                    images.append(f)
                elif file.lower().endswith((".desktop",)):
                    desktop.append(f)
                else:
                    files.append(f)
            else:
                dirPaths.append(f)

        dirPaths.sort()
        vids.sort()
        images.sort()
        desktop.sort()
        files.sort()
        files = dirPaths + vids + images + desktop + files

        if self.helperThread:
            self.helperThread.terminate()
            self.helperThread = None

        # Run helper thread...
        self.threadLock   = True
        self.helperThread = threading.Thread(target=self.generateDirectoryGridIcon, args=(path, files)).start()
        glib.idle_add(self.addToGrid, (file,))  # This must stay in the main thread b/c
                                                # gtk isn't thread safe/aware So, we
                                                # make a sad lil thread hot potato 'game'
                                                # out of this process.


    # @threaded
    def generateDirectoryGridIcon(self, dirPath, files):
        # NOTE: We'll be passing pixbuf after retreval to keep Icon.py file more
        # universaly usable. We can just remove get_pixbuf to get a gtk.Image type
        for file in files:
            image = Icon(self.settings).createIcon(dirPath, file)
            self.toWorkPool.append([image.get_pixbuf(), file])
            self.threadLock = False
            self.gtkLock    = True


    def addToGrid(self, args):
        # NOTE: Returning true tells gtk to check again in the future when idle.
        # False ends checks and "continues normal flow"
        files = args[0]

        if len(self.toWorkPool) > 0:
            for dataSet in self.toWorkPool:
                self.store.append(dataSet)

        if len(self.store) == len(files): # Confirm processed all files and cleanup
            self.gtkLock    = False
            self.threadLock = False
            self.toWorkPool.clear()
            return False
            # Check again when idle; If nothing else is updating, this function
            # gets called immediatly. So, we play hot potato by passing lock to Thread
        else:
            self.toWorkPool.clear()
            self.gtkLock    = False
            self.threadLock = True
            time.sleep(.005) # Fixes refresh and up icon not being added.
            return True

    def setIconSelectionArray(self, widget, data=None):
        pass
        # os.system('cls||clear')
        # print(data)

    def iconLeftClickEventManager(self, widget, item):
        try:
            model    = widget.get_model()
            fileName = model[item][1]
            dir      = self.currentPath
            file     = dir + "/" + fileName

            if fileName == ".":
                self.setIconViewDir(dir)
            elif fileName == "..":
                parentDir        = os.path.abspath(os.path.join(dir, os.pardir))
                self.currentPath = parentDir
                self.setIconViewDir(parentDir)
            elif isdir(file):
                self.currentPath = file
                self.setIconViewDir(self.currentPath)
            elif isfile(file):
                self.filehandler.openFile(file)
        except Exception as e:
            print(e)

    def iconRightClickEventManager(self, widget, eve, params):
        try:
            if eve.type == gdk.EventType.BUTTON_PRESS and eve.button == 3:
                popover = self.builder.get_object("iconControlsWindow")
                popover.show_all()
                popover.popup()
                # # NOTE: Need to change name of listview box...
                # children = widget.get_children()[0].get_children()
                # fileName = children[1].get_text()
                # dir      = self.currentPath
                # file     = dir + "/" + fileName
                #
                # input    = self.builder.get_object("iconRenameInput")
                # popover  = self.builder.get_object("iconControlsWindow")
                # self.selectedFile = file # Used for return to caller
                #
                # input.set_text(fileName)
                # popover.set_relative_to(widget)
                # popover.set_position(gtk.PositionType.RIGHT)
                # popover.show_all()
                # popover.popup()
        except Exception as e:
            print(e)


    # Passthrough file control events
    def createFile(arg):
        pass

    def updateFile(self, file):
        newName = self.currentPath + "/" + file
        status  = self.filehandler.updateFile(self.selectedFile, newName)

        if status == 0:
            self.selectedFile = newName
            self.setIconViewDir(self.currentPath)

    def deleteFile(self):
        status = self.filehandler.deleteFile(self.selectedFile)

        if status == 0:
            self.selectedFile = ""
            self.setIconViewDir(self.currentPath)

    def copyFile(self):
        pass

    def cutFile(self):
        pass

    def pasteFile(self):
        pass
