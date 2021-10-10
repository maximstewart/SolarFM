
# Gtk Imports

# Python imports
from .Grid     import Grid
from .Dragging import Dragging

class Events:
    def __init__(self, settings):
        self.settings     = settings
        self.builder      = self.settings.returnBuilder()
        self.desktop      = self.builder.get_object("Desktop")
        self.webview      = self.builder.get_object("webview")
        self.desktopPath  = self.settings.returnDesktopPath()

        self.settings.setDefaultWebviewSettings(self.webview, self.webview.get_settings())
        self.webview.load_uri(self.settings.returnWebHome())

        # Add filter to allow only folders to be selected
        selectedDirDialog = self.builder.get_object("selectedDirDialog")
        filefilter        = self.builder.get_object("Folders")
        selectedDirDialog.add_filter(filefilter)
        selectedDirDialog.set_filename(self.desktopPath)

        self.grid = None
        self.setIconViewDir(selectedDirDialog)

    def setIconViewDir(self, widget, data=None):
        newPath   = widget.get_filename()
        Grid(self.desktop, self.settings, newPath)



    # File control events
    def createFile(self):
        pass

    def updateFile(self, widget, data=None):
        newName = widget.get_text().strip()
        if data and data.keyval == 65293:    # Enter key event
            self.grid.updateFile(newName)
        elif data == None:                   # Save button 'event'
            self.grid.updateFile(newName)

    def deleteFile(self, widget, data=None):
        self.grid.deleteFile()

    def copyFile(self):
        pass

    def cutFile(self):
        pass

    def pasteFile(self):
        pass

    # Webview events
    def showWebview(self, widget):
        self.builder.get_object("webViewer").popup()

    def loadHome(self, widget):
        self.webview.load_uri(self.settings.returnWebHome())

    def runSearchWebview(self, widget, data=None):
        if data.keyval == 65293:
            self.webview.load_uri(widget.get_text().strip())

    def refreshPage(self, widget, data=None):
        self.webview.load_uri(self.webview.get_uri())

    def setUrlBar(self, widget, data=None):
        self.builder.get_object("webviewSearch").set_text(widget.get_uri())
