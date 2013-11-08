# Control Your Tabs, a plugin for gedit #

Switch between document tabs using Ctrl+Tab / Ctrl+Shift+Tab and
Ctrl+PageUp / Ctrl+PageDown  
<https://github.com/jefferyto/gedit-control-your-tabs>  
v0.2.3

All bug reports, feature requests and miscellaneous comments are welcome
at the [project issue tracker][].

## Requirements ##

v0.2.0 and higher requires at least gedit 3.2. (Untested with gedit 3.0;
it *may* work :-) )

gedit 2 users should use [v0.1.2][].

## Installation ##

1.  Download the source code (as [zip][] or [tar.gz][]) and extract.
2.  Copy the `controlyourtabs` folder and the appropriate `.plugin` file
    into `~/.local/share/gedit/plugins` (create if it does not exist):
    *   For gedit 3.6 and earlier, copy `controlyourtabs.plugin.python2`
        and rename to `controlyourtabs.plugin`.
    *   For gedit 3.8 and later, copy `controlyourtabs.plugin`.
3.  Restart gedit, select **Edit > Preferences** (or
    **gedit > Preferences** on Mac), and enable the plugin in the
    **Plugins** tab.

## Usage ##

*   <kbd>Ctrl</kbd>+<kbd>Tab</kbd> /
    <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>Tab</kbd> switch tabs in most
    recently used order.
*   <kbd>Ctrl</kbd>+<kbd>Page Up</kbd> /
    <kbd>Ctrl</kbd>+<kbd>Page Down</kbd> switch tabs in tabbar order.

## Development ##

The code in `controlyourtabs/utils` comes from [python-gtk-utils][];
changes should ideally be contributed to that project, then pulled back
into this one with `git subtree pull`.

## Credits ##

Inspired by:

*   [TabSwitch][] by Elia Sarti
*   [TabPgUpPgDown][] by Eran M.
*   the gedit Documents panel

## License ##

Copyright &copy; 2010-2013 Jeffery To <jeffery.to@gmail.com>

Available under GNU General Public License version 3


[project issue tracker]: https://github.com/jefferyto/gedit-control-your-tabs/issues
[zip]: https://github.com/jefferyto/gedit-control-your-tabs/archive/master.zip
[tar.gz]: https://github.com/jefferyto/gedit-control-your-tabs/archive/master.tar.gz
[v0.1.2]: https://github.com/jefferyto/gedit-control-your-tabs/archive/v0.1.2.zip
[python-gtk-utils]: https://github.com/jefferyto/python-gtk-utils
[TabSwitch]: https://wiki.gnome.org/Apps/Gedit/PluginsOld?action=AttachFile&do=view&target=tabswitch.tar.gz
[TabPgUpPgDown]: https://wiki.gnome.org/Apps/Gedit/PluginsOld?action=AttachFile&do=view&target=tabpgupdown.tar.gz
