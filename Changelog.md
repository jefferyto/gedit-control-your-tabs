# Changelog

## [v0.3.5-dev][Unreleased] - Unreleased

## [v0.3.4] - 2020-10-26
* Fixed AttributeError when loaded in gedit 3.38

## [v0.3.3] - 2020-05-13
* Added AppStream metainfo file ([#15][GH-15], thanks Artem Polishchuk)
* Fixed AttributeError when loaded in gedit 3.36 ([#17][GH-17])

## [v0.3.2] - 2018-03-13
* Added Ctrl-Esc to cancel tab switching, causes the initial tab (before
  switching began) to be active again
* Prevent all input during tab switching, if the tab switching window is
  visible, instead of cancelling switching
* Fixed copyright notices

## [v0.3.1] - 2017-10-17
* Show a debug message if the settings schema could not be loaded
* Fixed division by zero error

## [v0.3.0] - 2017-09-04
* Added a preference to change Ctrl-Tab to tabbar order, available
  in gedit 3.4 and later
* Made the tab window now sized and positioned more reliably
* Added translation support
* Handle the case when tab switching has started (e.g. Ctrl is held down
  after Tab is let go) and the user switches to different tabs using
  other means (e.g. clicking on document tabs or documents in the
  Documents panel)
* Fixed minor error if the plugin is enabled, disabled then enabled
  again in the same gedit session, and a new tab group is added
* Fixed minor error if the plugin is enabled, disabled then enabled
  again in the same gedit session, and a previously existing new
  document tab is replaced by an opened file, in gedit 3.14 or later
* Fixed minor error if a file icon needed to be resized in gedit 3.10 or
  earlier (originally fixed by nuclearmistake in [#8][GH-8])
* Ensure when the tab list popup appears it is scrolled to the top
* Made compatible with gedit 3.0
* Use python-gtk-utils for some plumbing

## [v0.2.3] - 2013-05-08
* Gedit 3.8 / Python 3 compatibility ([#4][GH-4], thanks thapar!)
* Minor tweaks

## [v0.2.2] - 2013-05-03
* Fixed minor bug when the document name contains HTML tags
* Minor tweaks

## [v0.2.1] - 2012-10-26
* Minor tweaks

## [v0.2.0] - 2011-11-18
* Works with, and requires, gedit 3.2

## v0.1.2 - 2010-06-21
* Fixed error when an icon cannot be loaded for a tab state (e.g. when
  an icon is missing from the current theme)

## v0.1.1 - 2010-03-03
* Fixed error when switching tabs after an open file has been deleted
  (but the tab is still open with the file)

## v0.1.0 - 2010-02-25
* Initial release


[Unreleased]: https://github.com/jefferyto/gedit-control-your-tabs/compare/v0.3.4...main
[v0.3.4]: https://github.com/jefferyto/gedit-control-your-tabs/compare/v0.3.3...v0.3.4
[v0.3.3]: https://github.com/jefferyto/gedit-control-your-tabs/compare/v0.3.2...v0.3.3
[v0.3.2]: https://github.com/jefferyto/gedit-control-your-tabs/compare/v0.3.1...v0.3.2
[v0.3.1]: https://github.com/jefferyto/gedit-control-your-tabs/compare/v0.3.0...v0.3.1
[v0.3.0]: https://github.com/jefferyto/gedit-control-your-tabs/compare/v0.2.3...v0.3.0
[v0.2.3]: https://github.com/jefferyto/gedit-control-your-tabs/compare/v0.2.2...v0.2.3
[v0.2.2]: https://github.com/jefferyto/gedit-control-your-tabs/compare/v0.2.1...v0.2.2
[v0.2.1]: https://github.com/jefferyto/gedit-control-your-tabs/compare/v0.2.0...v0.2.1
[v0.2.0]: https://github.com/jefferyto/gedit-control-your-tabs/compare/v0.1.2...v0.2.0

[GH-4]: https://github.com/jefferyto/gedit-control-your-tabs/pull/4
[GH-8]: https://github.com/jefferyto/gedit-control-your-tabs/pull/8
[GH-15]: https://github.com/jefferyto/gedit-control-your-tabs/pull/15
[GH-17]: https://github.com/jefferyto/gedit-control-your-tabs/issues/17
