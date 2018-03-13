# -*- coding: utf-8 -*-
#
# tabinfo.py
# This file is part of Control Your Tabs, a plugin for gedit
#
# Copyright (C) 2010-2013, 2017-2018 Jeffery To <jeffery.to@gmail.com>
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
from gi.repository import Gtk, GtkSource, Gedit
from xml.sax.saxutils import escape
from . import log

BASE_PATH = os.path.dirname(os.path.realpath(__file__))
LOCALE_PATH = os.path.join(BASE_PATH, 'locale')

try:
	import gettext
	gettext.bindtextdomain('gedit-control-your-tabs', LOCALE_PATH)
	_ = lambda s: gettext.dgettext('gedit-control-your-tabs', s)
except:
	_ = lambda s: s

try:
	debug_plugin_message = Gedit.debug_plugin_message
except: # before gedit 3.4
	debug_plugin_message = lambda fmt, *fmt_args: None


# based on switch statement in _gedit_tab_get_icon() in gedit-tab.c
TAB_STATE_TO_NAMED_ICON = {
	Gedit.TabState.STATE_PRINTING: 'printer-printing-symbolic',
	Gedit.TabState.STATE_PRINT_PREVIEWING: 'printer-symbolic',
	Gedit.TabState.STATE_SHOWING_PRINT_PREVIEW: 'printer-symbolic',
	Gedit.TabState.STATE_LOADING_ERROR: 'dialog-error-symbolic',
	Gedit.TabState.STATE_REVERTING_ERROR: 'dialog-error-symbolic',
	Gedit.TabState.STATE_SAVING_ERROR: 'dialog-error-symbolic',
	Gedit.TabState.STATE_GENERIC_ERROR: 'dialog-error-symbolic',
	Gedit.TabState.STATE_EXTERNALLY_MODIFIED_NOTIFICATION: 'dialog-warning-symbolic'
}

# based on doc_get_name() and document_row_sync_tab_name_and_icon() in gedit-documents-panel.c
def get_tab_name(tab):
	if log.query(log.INFO):
		debug_plugin_message(log.format("%s", tab))

	doc = tab.get_document()
	name = doc.get_short_name_for_display()
	docname = Gedit.utils_str_middle_truncate(name, 60) # based on MAX_DOC_NAME_LENGTH in gedit-documents-panel.c

	tab_format = "<b>%s</b>" if doc.get_modified() else "%s"
	tab_name = tab_format % escape(docname)

	try:
		file = doc.get_file()
		is_readonly = GtkSource.File.is_readonly(file)
	except AttributeError:
		is_readonly = doc.get_readonly() # deprecated since gedit 3.18

	if is_readonly:
		tab_name += " [%s]" % escape(_("Read-Only"))

	if log.query(log.DEBUG):
		debug_plugin_message(log.format("tab_name=%s", tab_name))

	return tab_name

# based on _gedit_tab_get_icon() in gedit-tab.c
def get_tab_icon(tab):
	if log.query(log.INFO):
		debug_plugin_message(log.format("%s", tab))

	state = tab.get_state()

	if state not in TAB_STATE_TO_NAMED_ICON:
		return None

	theme = Gtk.IconTheme.get_for_screen(tab.get_screen())
	icon_name = TAB_STATE_TO_NAMED_ICON[state]
	icon_size = get_tab_icon_size(tab)

	return Gtk.IconTheme.load_icon(theme, icon_name, icon_size, 0)

def get_tab_icon_size(tab):
	if log.query(log.INFO):
		debug_plugin_message(log.format("%s", tab))

	is_valid_size, icon_size_width, icon_size_height = Gtk.icon_size_lookup(Gtk.IconSize.MENU)

	return icon_size_height

