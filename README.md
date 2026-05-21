# HEXMANAGER 
**This is an experimental manager based on the Qt framework and written in PySide6**
## Description
HEXManager allows you to write plugins that are automatically included. 
It provides a special base structure for plugins, and within the plugin itself, you can create anything you want, as long as the basic architecture is preserved. For this purpose, the PluginBase class exists in core.py. All plugins must be children of PluginBase to maintain stable operation.

## Writing plugin
To use it, you need to install the HEXManager basement; you can safely delete the base plugins. 

Clone the repository to the desired folder:
`git clone https://github.com/TechnoWizardX/HEXManager`

By default, there's a plugin called .example. It contains all the basic content for the plugin. It's best not to change it =D.
You can safely add new files, but you should not change existing ones from the base one.

Now, let's go to writing your plugin
1. Check: don't forget you to clone repository
2. Go to src -> plugins 
3. Ctrl C + Ctrl V .example plugin folder
4. Rename it as you like
5. Open plugin.json and make sure, that it looks like that:
```
{
  "id": "",
  "name": "",
  "display_name": "",
  "entry_point": "",
  "version": "",
  "author": "",
  "description": "",
  "icon": "",

  "theme_overrides": {
  }
}
```
You need to fill in information about your plugin. Let me explain what is there:
- "id" - This is unique identifier for plugin. If manager meet 2 plugins with one id, it make conflict, and one of them will not be showe
- "name" - This is first name of plugin. To be honestly, i don't remember for what that, but if it didn't exists, your plugin will not show 
- "display_name" - This is second name of Plugin. Shows instead of "name" if it exists
- "entry_point" - This is where your plugin starts. If you want the plugin to work correctly, it's better not to change it.
- "version" - This is version of your plugin
- "author" - I think it's clear what should be here
- "icon" - This is path to plugin icon. It too better not change but not critical
- "theme_overrides" - The most interesting thing. There you write your plugin color if it have. You should use basic architecture of HEXManager theme managing, but if you want, you can change (I do not guarantee that it will work correctly.)