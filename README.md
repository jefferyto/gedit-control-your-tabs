# Control Your Tabs, a plugin for gedit

Switch between document tabs using Ctrl+Tab / Ctrl+Shift+Tab and
Ctrl+PageUp / Ctrl+PageDown  
<https://github.com/jefferyto/gedit-control-your-tabs>  
v0.3.2

All bug reports, feature requests and miscellaneous comments are welcome
at the [project issue tracker][].

## Requirements

v0.2.0 and higher requires gedit 3. The last version compatible with
gedit 2 is [v0.1.2][].

## Installation

1.  Download the source code (as [zip][] or [tar.gz][]) and extract.
2.  Copy the `controlyourtabs` folder and the appropriate `.plugin` file
    into `~/.local/share/gedit/plugins` (create if it does not exist):
    *   For gedit 3.6 and earlier, copy `controlyourtabs.plugin.python2`
        and rename to `controlyourtabs.plugin`.
    *   For gedit 3.8 and later, copy `controlyourtabs.plugin`.
3.  Restart gedit, then activate the plugin in the **Plugins** tab in
    gedit's **Preferences** window.
	
### Packages

- [Fedora (official repo)](https://apps.fedoraproject.org/packages/gedit-control-your-tabs) (29, 30 and Rawhide): `sudo dnf install gedit-control-your-tabs`

## Usage

*   <kbd>Ctrl</kbd>+<kbd>Tab</kbd> /
    <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>Tab</kbd> - Switch tabs in
    most recently used order.
*   <kbd>Ctrl</kbd>+<kbd>Page Up</kbd> /
    <kbd>Ctrl</kbd>+<kbd>Page Down</kbd> - Switch tabs in tab row order.

Hold down <kbd>Ctrl</kbd> to continue tab switching. Press
<kbd>Esc</kbd> while switching to cancel and return to the initial tab.

## Preferences

In gedit 3.4 or later, the plugin supports these preferences:

*   `Use tab row order for Ctrl+Tab / Ctrl+Shift+Tab` - Change
    <kbd>Ctrl</kbd>+<kbd>Tab</kbd> /
    <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>Tab</kbd> to switch tabs in
    tab row order instead of most recently used order.

## Contributing

Please base changes on, and open pull requests against, the `develop`
branch.

The code in `controlyourtabs/utils` comes from [python-gtk-utils][];
changes should ideally be contributed to that project, then pulled back
into this one with `git subtree pull`.

## Credits

Inspired by:

*   [TabSwitch][] by Elia Sarti
*   [TabPgUpPgDown][] by Eran M.
*   the gedit Documents panel

## License

Copyright &copy; 2010-2013, 2017-2018 Jeffery To <jeffery.to@gmail.com>

Available under GNU General Public License version 3


[project issue tracker]: https://github.com/jefferyto/gedit-control-your-tabs/issues
[zip]: https://github.com/jefferyto/gedit-control-your-tabs/archive/master.zip
[tar.gz]: https://github.com/jefferyto/gedit-control-your-tabs/archive/master.tar.gz
[v0.1.2]: https://github.com/jefferyto/gedit-control-your-tabs/archive/v0.1.2.zip
[python-gtk-utils]: https://github.com/jefferyto/python-gtk-utils
[TabSwitch]: https://wiki.gnome.org/Apps/Gedit/PluginsOld?action=AttachFile&do=view&target=tabswitch.tar.gz
[TabPgUpPgDown]: https://wiki.gnome.org/Apps/Gedit/PluginsOld?action=AttachFile&do=view&target=tabpgupdown.tar.gz
