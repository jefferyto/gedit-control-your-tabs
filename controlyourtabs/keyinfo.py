# -*- coding: utf-8 -*-
#
# keyinfo.py
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

from gi.repository import Gtk, Gdk, Gedit
from . import log

try:
	debug_plugin_message = Gedit.debug_plugin_message
except: # before gedit 3.4
	debug_plugin_message = lambda fmt, *fmt_args: None


CONTROL_MASK = Gdk.ModifierType.CONTROL_MASK

CONTROL_SHIFT_MASK = Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.SHIFT_MASK

CONTROL_KEY_LIST = [Gdk.KEY_Control_L, Gdk.KEY_Control_R] # will need to iterate through this list

TAB_KEY_SET = set([Gdk.KEY_ISO_Left_Tab, Gdk.KEY_Tab])

PAGE_KEY_SET = set([Gdk.KEY_Page_Up, Gdk.KEY_Page_Down])

NEXT_KEY_SET = set([Gdk.KEY_Tab, Gdk.KEY_Page_Down])

ESCAPE_KEY = Gdk.KEY_Escape


def default_control_held():
	return [False for control_key in CONTROL_KEY_LIST]

def update_control_held(event, prev_statuses, new_status):
	keyval = event.keyval

	if log.query(log.INFO):
		debug_plugin_message(log.format("key=%s, %s, new_status=%s", Gdk.keyval_name(keyval), prev_statuses, new_status))

	new_statuses = [
		new_status if keyval == control_key else prev_status
		for control_key, prev_status in zip(CONTROL_KEY_LIST, prev_statuses)
	]

	if log.query(log.DEBUG):
		debug_plugin_message(log.format("new_statuses=%s", new_statuses))

	return new_statuses

def is_control_keys(event):
	keyval = event.keyval
	state = event.state & Gtk.accelerator_get_default_mod_mask()

	if log.query(log.INFO):
		debug_plugin_message(log.format("key=%s, state=%s", Gdk.keyval_name(keyval), state))

	is_control = state == CONTROL_MASK
	is_control_shift = state == CONTROL_SHIFT_MASK

	is_tab = keyval in TAB_KEY_SET
	is_page = keyval in PAGE_KEY_SET
	is_escape = keyval == ESCAPE_KEY

	is_control_tab = (is_control or is_control_shift) and is_tab
	is_control_page = is_control and is_page
	is_control_escape = (is_control or is_control_shift) and is_escape

	if log.query(log.DEBUG):
		debug_plugin_message(log.format("is_control_tab=%s, is_control_page=%s, is_control_escape=%s", is_control_tab, is_control_page, is_control_escape))

	return (is_control_tab, is_control_page, is_control_escape)

def is_next_key(event):
	if log.query(log.INFO):
		debug_plugin_message(log.format("key=%s", Gdk.keyval_name(event.keyval)))

	result = event.keyval in NEXT_KEY_SET

	if log.query(log.DEBUG):
		debug_plugin_message(log.format("result=%s", result))

	return result

