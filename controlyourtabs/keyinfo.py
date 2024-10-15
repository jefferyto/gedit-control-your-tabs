# -*- coding: utf-8 -*-
#
# keyinfo.py
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
gi.require_version('Gdk', '3.0')
gi.require_version('Gtk', '3.0')

from collections import namedtuple
from gi.repository import Gdk, Gtk
from . import editor, log


CONTROL_MASK = Gdk.ModifierType.CONTROL_MASK

CONTROL_SHIFT_MASK = Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.SHIFT_MASK

CONTROL_KEY_LIST = [Gdk.KEY_Control_L, Gdk.KEY_Control_R] # will need to iterate through this list

KEY_SETS = {
	'tab': set([Gdk.KEY_ISO_Left_Tab, Gdk.KEY_Tab, Gdk.KEY_KP_Tab]), # what is shift numpad tab?
	'page_up': set([Gdk.KEY_Page_Up, Gdk.KEY_KP_Page_Up]),
	'page_down': set([Gdk.KEY_Page_Down, Gdk.KEY_KP_Page_Down]),
	'escape': set([Gdk.KEY_Escape])
}

MODIFIER_KEY_SET = set(
	[
		Gdk.KEY_Shift_L, Gdk.KEY_Shift_R,
		Gdk.KEY_Control_L, Gdk.KEY_Control_R,
		Gdk.KEY_Meta_L, Gdk.KEY_Meta_R,
		Gdk.KEY_Alt_L, Gdk.KEY_Alt_R,
		Gdk.KEY_Super_L, Gdk.KEY_Super_R,
		Gdk.KEY_Hyper_L, Gdk.KEY_Hyper_R,
		Gdk.KEY_Caps_Lock, Gdk.KEY_Shift_Lock, Gdk.KEY_Num_Lock, Gdk.KEY_Scroll_Lock,
		Gdk.KEY_ISO_Lock, Gdk.KEY_ISO_Level2_Latch,
		Gdk.KEY_ISO_Level3_Shift, Gdk.KEY_ISO_Level3_Latch, Gdk.KEY_ISO_Level3_Lock,
		Gdk.KEY_ISO_Level5_Shift, Gdk.KEY_ISO_Level5_Latch, Gdk.KEY_ISO_Level5_Lock,
		Gdk.KEY_Mode_switch
	]
)

ControlKeys = namedtuple(
	'ControlKeys',
	[
		*[key for key in KEY_SETS.keys()],
		*['shift_' + key for key in KEY_SETS.keys()],
		*[key + '_key' for key in KEY_SETS.keys()]
	]
)


def default_control_held():
	return [False for control_key in CONTROL_KEY_LIST]

def update_control_held(event, prev_statuses, new_status):
	keyval = event.keyval

	if log.query(log.DEBUG):
		editor.debug_plugin_message(log.format("key=%s, %s, new_status=%s", Gdk.keyval_name(keyval), prev_statuses, new_status))

	new_statuses = [
		new_status if keyval == control_key else prev_status
		for control_key, prev_status in zip(CONTROL_KEY_LIST, prev_statuses)
	]

	if log.query(log.DEBUG):
		editor.debug_plugin_message(log.format("new_statuses=%s", new_statuses))

	return new_statuses

def is_control_keys(event):
	keyval = event.keyval
	state = event.state & Gtk.accelerator_get_default_mod_mask()

	if log.query(log.DEBUG):
		editor.debug_plugin_message(log.format("key=%s, state=%s", Gdk.keyval_name(keyval), state))

	is_control = state == CONTROL_MASK
	is_control_shift = state == CONTROL_SHIFT_MASK
	is_control_key = is_control or is_control_shift

	is_key = {key: keyval in set for (key, set) in KEY_SETS.items()}

	result = ControlKeys(**{
		**{key: value and is_control for (key, value) in is_key.items()},
		**{'shift_' + key: value and is_control_shift for (key, value) in is_key.items()},
		**{key + '_key': value and is_control_key for (key, value) in is_key.items()}
	})

	if log.query(log.DEBUG):
		editor.debug_plugin_message(log.format("result=%s", result))

	return result

def is_modifier_key(event):
	if log.query(log.DEBUG):
		editor.debug_plugin_message(log.format("key=%s", Gdk.keyval_name(event.keyval)))

	result = event.keyval in MODIFIER_KEY_SET

	if log.query(log.DEBUG):
		editor.debug_plugin_message(log.format("result=%s", result))

	return result

