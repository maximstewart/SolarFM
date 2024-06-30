### Note
Copy the example and rename it to your desired name. Plugins define a ui target slot with the 'ui_target' requests data but don't have to if not directly interacted with.
Plugins must have a run method defined; though, you do not need to necessarily do anything within it. The run method implies that the passed in event system or other data is ready for the plugin to use.


### Manifest Example (All are required even if empty.)
```
class Manifest:
    name: str     = "Example Plugin"
    author: str   = "John Doe"
    version: str  = "0.0.1"
    support: str  = ""
    requests: {}  = {
        'ui_target': "plugin_control_list",
        'pass_fm_events': "true"
    }
    pre_launch: bool = False
```


### Requests
```
requests: {}  = {
    'ui_target': "plugin_control_list",
    'ui_target_id': "<some other Gtk Glade ID>",          # Only needed if using "other" in "ui_target". See below for predefined "ui_target" options...
    'pass_fm_events': "true",                             # If empty or not present will be ignored.
    "pass_ui_objects": [""],                              # Request reference to a UI component. Will be passed back as array to plugin.
    'bind_keys': [f"{name}||send_message:<Control>f"],
                  f"{name}||do_save:<Control>s"]          # Bind keys with method and key pare using list. Must pass "name" like shown with delimiter to its right.

}
```

UI Targets:
<ul>
<li>main_Window</li>
<li>main_menu_bar</li>
<li>path_menu_bar</li>
<li>plugin_control_list</li>
<li>window_(1-4)</li>
<li>context_menu</li>
<li>other</li>
</ul>
