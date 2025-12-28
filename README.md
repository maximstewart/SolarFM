# SolarFM
SolarFM is a Gtk+ Python file manager.

# Notes
If not building a .deb then just move the contents of user_config to their respective folders.
Copy the share/solarfm folder to your user .config/ directory too.

`pyrightconfig.json`
<p>The pyrightconfig file needs to stay on same level as the .git folders in order to have settings detected when using pyright with lsp functionality. "pyrightconfig.json" can prompt IDEs such as Zed on settings to use and where imports are located- look at venvPath and venv. "venvPath" is parent path of "venv" where "venv" is just the name of the folder under the parent path that is the python created venv.

<h6>Install Setup</h6>
```
sudo apt-get install xclip python3.8 python3-setproctitle python3-gi wget ffmpegthumbnailer steamcmd
```

# Known Issues
<ul>
<li>There is a memory leak that has been slowed down but can get to 2GB over a long enough time period OR active accessing image based dirs.</li>
<li>Doing Ctrl+D when in Terminator (maybe other terminals too) somehow propagates the signal to SolarFM too.
A selected file in the active quad-pane will move to trash since it is the default key-binding for that action.</li>
</ul>

# TODO
<ul>
<li>Add simpleish preview plugin for various file types.</li>
</ul>

# Images
![1 SolarFM single pane. ](images/pic1.png)
![2 SolarFM double pane. ](images/pic2.png)
![3 SolarFM triple pane. ](images/pic3.png)
![4 SolarFM quad pane. ](images/pic4.png)
