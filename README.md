# Control Your Tabs, a plugin for gedit, Pluma, and xed

Switch between document tabs using Ctrl+Tab and other common keyboard
shortcuts  
<https://github.com/jefferyto/gedit-control-your-tabs>  
v0.5.2-dev

All bug reports, feature requests, and miscellaneous comments are
welcome at the [project issue tracker].

Be sure to watch the project on GitHub to receive notifications for new
releases.

[project issue tracker]: https://github.com/jefferyto/gedit-control-your-tabs/issues

## Requirements

This plugin requires one of these text editors:

*   gedit 3.12 to 48.1
*   Pluma 1.26.0 or later
*   xed 1.4.0 or later

The last version compatible with gedit 2 is [v0.1.2], and the last
version compatible with gedit 3.0 to 3.10 is [v0.3.5].

[v0.1.2]: https://github.com/jefferyto/gedit-control-your-tabs/releases/tag/v0.1.2
[v0.3.5]: https://github.com/jefferyto/gedit-control-your-tabs/releases/tag/v0.3.5

## Installation

1.  Download the [latest release] and extract.
2.  Copy the `controlyourtabs` folder and the `controlyourtabs.plugin`
    file into one of these paths (create if it does not exist):
    * gedit: `~/.local/share/gedit/plugins`
    * Pluma: `~/.local/share/pluma/plugins`
    * xed: `~/.local/share/xed/plugins`
3.  Restart the text editor, then activate the plugin in the **Plugins**
    tab of the text editor’s **Preferences** window.

[latest release]: https://github.com/jefferyto/gedit-control-your-tabs/releases/latest

### Packages

*   [Fedora (official repo)] (Fedora 29 to 42):
    `sudo dnf install gedit-control-your-tabs`

[Fedora (official repo)]: https://packages.fedoraproject.org/pkgs/gedit-control-your-tabs/gedit-control-your-tabs

## Usage

This plugin adds the following keyboard shortcuts:

| Action                                | Shortcut                                                  |
| :------------------------------------ | :-------------------------------------------------------- |
| Switch to next most recently used tab | <kbd>Ctrl</kbd> + <kbd>Tab</kbd>                          |
| Switch to tab on the left             | <kbd>Ctrl</kbd> + <kbd>Page Up</kbd>                      |
| Switch to tab on the right            | <kbd>Ctrl</kbd> + <kbd>Page Down</kbd>                    |
| Move current tab left                 | <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>Page Up</kbd>   |
| Move current tab right                | <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>Page Down</kbd> |

Hold down <kbd>Ctrl</kbd> to continue tab switching. Press
<kbd>Esc</kbd> while holding <kbd>Ctrl</kbd> to cancel and return to the
initial tab.

## Preferences

*   `Ctrl+Tab and Ctrl+Shift+Tab switch to tabs on the left and right`

    Change <kbd>Ctrl</kbd> + <kbd>Tab</kbd> and <kbd>Ctrl</kbd> +
    <kbd>Shift</kbd> + <kbd>Tab</kbd> to switch to tabs on the left and
    right instead of in most recently used order.

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

Copyright © 2010-2013, 2017-2018, 2020, 2023-2024 Jeffery To <jeffery.to@gmail.com>

Available under GNU General Public License version 2 or later

## Other plugins you may like

*   [Ex-Mortis] (gedit only)  
    Reopen closed windows and optionally restore windows between sessions

*   [Python Console]  
    Interactive Python console standing in the bottom panel

*   [Tab Group Salute] (gedit only)  
    Switch between tab groups using Ctrl+\<key above Tab\>

[Ex-Mortis]: https://github.com/jefferyto/gedit-ex-mortis
[Python Console]: https://github.com/jefferyto/gedit-pythonconsole
[Tab Group Salute]: https://github.com/jefferyto/gedit-tab-group-salute
