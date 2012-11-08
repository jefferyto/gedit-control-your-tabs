# Control Your Tabs, a plugin for gedit #

Switch between document tabs using Ctrl+Tab / Ctrl+Shift+Tab and
Ctrl+PageUp / Ctrl+PageDown  
<https://github.com/jefferyto/gedit-control-your-tabs>  
v0.2.1

All bug reports, feature requests and miscellaneous comments are welcome
at the [project issue tracker][].

## Requirements ##

v0.2.0 and higher requires at least gedit 3.2. (Untested with gedit 3.0;
it *may* work :-) )

gedit 2 users should use [v0.1.2][].

## Installation ##

1.  Download the source code (as [zip][] or [tar.gz][]) and extract.
2.  Copy `controlyourtabs.plugin` and `controlyourtabs.py` into
    `~/.local/share/gedit/plugins` (create if it does not exist).
3.  Restart gedit, select **Edit > Preferences** (or
    **gedit > Preferences** on Mac), and enable the plugin in the
    **Plugins** tab.

## Usage ##

*   Ctrl+Tab / Ctrl+Shift+Tab switch tabs in most recently used order.
*   Ctrl+PageUp / Ctrl+PageDown switch tabs in tabbar order.

## Credits ##

Inspired by:

*   [TabSwitch][] by Elia Sarti
*   [TabPgUpPgDown][] by Eran M.
*   the gedit Documents panel

## License ##

Copyright &copy; 2010-2012 Jeffery To <jeffery.to@gmail.com>

Available under GNU General Public License version 3


[project issue tracker]: https://github.com/jefferyto/gedit-control-your-tabs/issues
[zip]: https://github.com/jefferyto/gedit-control-your-tabs/archive/master.zip
[tar.gz]: https://github.com/jefferyto/gedit-control-your-tabs/archive/master.tar.gz
[v0.1.2]: https://github.com/jefferyto/gedit-control-your-tabs/archive/v0.1.2.zip
[TabSwitch]: http://live.gnome.org/Gedit/Plugins?action=AttachFile&do=get&target=tabswitch.tar.gz
[TabPgUpPgDown]: http://live.gnome.org/Gedit/Plugins?action=AttachFile&do=get&target=tabpgupdown.tar.gz
