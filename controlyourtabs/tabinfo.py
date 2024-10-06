# -*- coding: utf-8 -*-
#
# tabinfo.py
# This file is part of Control Your Tabs, a plugin for gedit
#
# Copyright (C) 2010-2013, 2017-2018, 2020, 2023-2024 Jeffery To <jeffery.to@gmail.com>
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

import gi
gi.require_version('Gtk', '3.0')
# GtkSource can be version 3 or 4 or 300

import os.path
from gi.repository import Gtk, GtkSource
from xml.sax.saxutils import escape
from .plugin import _
from . import editor, log


# based on switch statement in _gedit_tab_get_icon() in gedit-tab.c
STATE_ICONS = {
	'PRINTING': 'document-print',
	'PRINT_PREVIEWING': 'document-print-preview', # removed in gedit 3.36
	'SHOWING_PRINT_PREVIEW': 'document-print-preview',
	'LOADING_ERROR': 'dialog-error',
	'REVERTING_ERROR': 'dialog-error',
	'SAVING_ERROR': 'dialog-error',
	'GENERIC_ERROR': 'dialog-error',
	'EXTERNALLY_MODIFIED_NOTIFICATION': 'dialog-warning'
}

TAB_STATE_ICONS = {}
for state_name, icon_name in STATE_ICONS.items():
	state = None
	if hasattr(editor.Editor.TabState, state_name):
		state = getattr(editor.Editor.TabState, state_name)
	elif hasattr(editor.Editor.TabState, 'STATE_' + state_name): # before gedit 47
		state = getattr(editor.Editor.TabState, 'STATE_' + state_name)

	if editor.use_symbolic_icons:
		icon_name += '-symbolic'

	if state:
		TAB_STATE_ICONS[state] = icon_name

# based on doc_get_name() and document_row_sync_tab_name_and_icon() in gedit-documents-panel.c
def get_tab_name(tab):
	if log.query(log.INFO):
		editor.debug_plugin_message(log.format("%s", tab))

	doc = tab.get_document()
	is_modified = doc.get_modified()
	name = tab.get_property('name')
	if is_modified and name[0] == "*":
		name = name[1:]

	if is_modified:
		name_format = '<b>%s</b>' if editor.use_new_tab_name_style else '<i>%s</i>'
	else:
		name_format = '%s'
	tab_name = name_format % escape(name)

	try:
		file = doc.get_file()
		is_readonly = GtkSource.File.is_readonly(file)
	except AttributeError:
		is_readonly = doc.get_readonly() # deprecated since gedit 3.18

	if is_readonly:
		readonly_format = '%s' if editor.use_new_tab_name_style else '<i>%s</i>'
		readonly_text = readonly_format % escape(_("Read-Only"))
		tab_name += ' [%s]' % readonly_text

	if log.query(log.DEBUG):
		editor.debug_plugin_message(log.format("tab_name=%s", tab_name))

	return tab_name

# based on _gedit_tab_get_icon() in gedit-tab.c
def get_tab_icon(tab):
	if log.query(log.INFO):
		editor.debug_plugin_message(log.format("%s", tab))

	state = tab.get_state()

	if state not in TAB_STATE_ICONS:
		return None

	theme = Gtk.IconTheme.get_for_screen(tab.get_screen())
	icon_name = TAB_STATE_ICONS[state]
	icon_size = get_tab_icon_size(tab)

	return Gtk.IconTheme.load_icon(theme, icon_name, icon_size, 0)

def get_tab_icon_size(tab):
	if log.query(log.INFO):
		editor.debug_plugin_message(log.format("%s", tab))

	is_valid_size, icon_size_width, icon_size_height = Gtk.icon_size_lookup(Gtk.IconSize.MENU)

	return icon_size_height

