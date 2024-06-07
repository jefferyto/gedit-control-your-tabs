# Control Your Tabs, a plugin for gedit

Switch between document tabs using Ctrl+Tab / Ctrl+Shift+Tab and
Ctrl+PageUp / Ctrl+PageDown  
<https://github.com/jefferyto/gedit-control-your-tabs>  
v0.4.1

All bug reports, feature requests, and miscellaneous comments are
welcome at the [project issue tracker].

Be sure to watch the project on GitHub to receive notifications for new
releases.

[project issue tracker]: https://github.com/jefferyto/gedit-control-your-tabs/issues

## Requirements

This plugin requires gedit 3.12 or newer. The last version compatible
with gedit 2 is [v0.1.2], and the last version compatible with gedit
3.0-3.10 is [v0.3.5].

[v0.1.2]: https://github.com/jefferyto/gedit-control-your-tabs/releases/tag/v0.1.2
[v0.3.5]: https://github.com/jefferyto/gedit-control-your-tabs/releases/tag/v0.3.5

## Installation

1.  Download the [latest release] and extract.
2.  Copy the `controlyourtabs` folder and the `controlyourtabs.plugin`
    file into `~/.local/share/gedit/plugins` (create if it does not
    exist).
3.  Restart gedit, then activate the plugin in the **Plugins** tab in
    gedit's **Preferences** window.

[latest release]: https://github.com/jefferyto/gedit-control-your-tabs/releases/latest

### Packages

*   [Fedora (official repo)] (Fedora 29 and later, Rawhide):
    `sudo dnf install gedit-control-your-tabs`

[Fedora (official repo)]: https://apps.fedoraproject.org/packages/gedit-control-your-tabs

## Usage

*   <kbd>Ctrl</kbd>+<kbd>Tab</kbd> /
    <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>Tab</kbd> - Switch tabs in
    most recently used order.
*   <kbd>Ctrl</kbd>+<kbd>Page Up</kbd> /
    <kbd>Ctrl</kbd>+<kbd>Page Down</kbd> - Switch tabs in tab row order.

Hold down <kbd>Ctrl</kbd> to continue tab switching. Press
<kbd>Esc</kbd> while switching to cancel and return to the initial tab.

## Preferences

*   `Use tab row order for Ctrl+Tab / Ctrl+Shift+Tab` - Change
    <kbd>Ctrl</kbd>+<kbd>Tab</kbd> /
    <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>Tab</kbd> to switch tabs in
    tab row order instead of most recently used order.

## Contributing

The code in `controlyourtabs/utils` comes from [python-gtk-utils];
changes should ideally be contributed to that project, then pulled back
into this one with `git subtree pull`.

[python-gtk-utils]: https://github.com/jefferyto/python-gtk-utils

## Credits

Inspired by:

*   [TabSwitch] by Elia Sarti
*   [TabPgUpPgDown] by Eran M.
*   the gedit Documents panel

[TabSwitch]: https://wiki.gnome.org/Apps/Gedit/PluginsOld?action=AttachFile&do=view&target=tabswitch.tar.gz
[TabPgUpPgDown]: https://wiki.gnome.org/Apps/Gedit/PluginsOld?action=AttachFile&do=view&target=tabpgupdown.tar.gz

## License

Copyright &copy; 2010-2013, 2017-2018, 2020, 2023-2024 Jeffery To <jeffery.to@gmail.com>

Available under GNU General Public License version 3
