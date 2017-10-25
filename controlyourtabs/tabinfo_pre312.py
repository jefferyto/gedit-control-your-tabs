# -*- coding: utf-8 -*-
#
# tabinfo_pre312.py
# This file is part of Control Your Tabs, a plugin for gedit
#
# Copyright (C) 2010-2013, 2017 Jeffery To <jeffery.to@gmail.com>
# https://github.com/jefferyto/gedit-control-your-tabs
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os.path
from gi.repository import GObject, Gtk, GdkPixbuf, Gio, Gedit
from xml.sax.saxutils import escape

BASE_PATH = os.path.dirname(os.path.realpath(__file__))
LOCALE_PATH = os.path.join(BASE_PATH, 'locale')

try:
	import gettext
	gettext.bindtextdomain('gedit-control-your-tabs', LOCALE_PATH)
	_ = lambda s: gettext.dgettext('gedit-control-your-tabs', s)
except:
	_ = lambda s: s


# based on switch statement in _gedit_tab_get_icon() in gedit-tab.c
TAB_STATE_TO_STOCK_ICON = {
	Gedit.TabState.STATE_LOADING: Gtk.STOCK_OPEN,
	Gedit.TabState.STATE_REVERTING: Gtk.STOCK_REVERT_TO_SAVED,
	Gedit.TabState.STATE_SAVING: Gtk.STOCK_SAVE,
	Gedit.TabState.STATE_PRINTING: Gtk.STOCK_PRINT,
	Gedit.TabState.STATE_PRINT_PREVIEWING: Gtk.STOCK_PRINT_PREVIEW,
	Gedit.TabState.STATE_SHOWING_PRINT_PREVIEW: Gtk.STOCK_PRINT_PREVIEW,
	Gedit.TabState.STATE_LOADING_ERROR: Gtk.STOCK_DIALOG_ERROR,
	Gedit.TabState.STATE_REVERTING_ERROR: Gtk.STOCK_DIALOG_ERROR,
	Gedit.TabState.STATE_SAVING_ERROR: Gtk.STOCK_DIALOG_ERROR,
	Gedit.TabState.STATE_GENERIC_ERROR: Gtk.STOCK_DIALOG_ERROR,
	Gedit.TabState.STATE_EXTERNALLY_MODIFIED_NOTIFICATION: Gtk.STOCK_DIALOG_WARNING
}

# based on tab_get_name() in gedit-documents-panel.c
def get_tab_name(tab):
	doc = tab.get_document()
	name = doc.get_short_name_for_display()
	docname = Gedit.utils_str_middle_truncate(name, 60) # based on MAX_DOC_NAME_LENGTH in gedit-documents-panel.c

	tab_format = "<i>%s</i>" if doc.get_modified() else "%s"
	tab_name = tab_format % escape(docname)

	if doc.get_readonly():
		tab_name += " [<i>%s</i>]" % escape(_("Read-Only"))

	return tab_name

# based on _gedit_tab_get_icon() in gedit-tab.c
def get_tab_icon(tab):
	state = tab.get_state()
	theme = Gtk.IconTheme.get_for_screen(tab.get_screen())
	icon_size = get_tab_icon_size(tab)
	pixbuf = None

	if state in TAB_STATE_TO_STOCK_ICON:
		try:
			pixbuf = get_stock_icon(theme, TAB_STATE_TO_STOCK_ICON[state], icon_size)
		except GObject.GError:
			pixbuf = None

	if not pixbuf:
		pixbuf = get_icon(theme, tab.get_document().get_location(), icon_size)

	return pixbuf

def get_tab_icon_size(tab):
	is_valid_size, icon_size_width, icon_size_height = Gtk.icon_size_lookup_for_settings(tab.get_settings(), Gtk.IconSize.MENU)
	return icon_size_height

# based on get_stock_icon() in gedit-tab.c
def get_stock_icon(theme, stock, size):
	pixbuf = theme.load_icon(stock, size, 0)
	return resize_icon(pixbuf, size)

# based on get_icon() in gedit-tab.c
def get_icon(theme, location, size):
	pixbuf = None

	if location:
		# FIXME: Doing a sync stat is bad, this should be fixed
		try:
			info = location.query_info(Gio.FILE_ATTRIBUTE_STANDARD_ICON, Gio.FileQueryInfoFlags.NONE, None)
		except GObject.GError:
			info = None

		icon = info.get_icon() if info else None
		icon_info = theme.lookup_by_gicon(icon, size, 0) if icon else None
		pixbuf = icon_info.load_icon() if icon_info else None

	if pixbuf:
		pixbuf = resize_icon(pixbuf, size)
	else:
		pixbuf = get_stock_icon(theme, Gtk.STOCK_FILE, size)

	return pixbuf

# based on resize_icon() in gedit-tab.c
def resize_icon(pixbuf, size):
	width = pixbuf.get_width()
	height = pixbuf.get_height()

	# if the icon is larger than the nominal size, scale down
	if max(width, height) > size:
		if width > height:
			height = height * size / width
			width = size
		else:
			width = width * size / height
			height = size

		pixbuf = pixbuf.scale_simple(width, height, GdkPixbuf.InterpType.BILINEAR)

	return pixbuf

