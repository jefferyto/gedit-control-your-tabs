# -*- coding: utf-8 -*-
#
# log.py
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

import os
from gi.repository import GLib
from .utils import debug_str


# for convenience, in decreasing order of severity
ERROR = GLib.LogLevelFlags.LEVEL_ERROR
CRITICAL = GLib.LogLevelFlags.LEVEL_CRITICAL
WARNING = GLib.LogLevelFlags.LEVEL_WARNING
MESSAGE = GLib.LogLevelFlags.LEVEL_MESSAGE
INFO = GLib.LogLevelFlags.LEVEL_INFO
DEBUG = GLib.LogLevelFlags.LEVEL_DEBUG

LEVELS_TO_NAMES = {
	ERROR: "error",
	CRITICAL: "critical",
	WARNING: "warning",
	MESSAGE: "message",
	INFO: "info",
	DEBUG: "debug"
}

NAMES_TO_LEVELS = {}

for (level, name) in LEVELS_TO_NAMES.items():
	NAMES_TO_LEVELS[name] = level

# messages equal or higher in severity will be printed
output_level = MESSAGE

name = os.getenv('GEDIT_CONTROL_YOUR_TABS_DEBUG_LEVEL', '').lower()
if name in NAMES_TO_LEVELS:
	output_level = NAMES_TO_LEVELS[name]

# set by query(), used by name()
last_queried_level = None


def is_error(log_level):
	return bool(log_level & ERROR)

def is_critical(log_level):
	return bool(log_level & CRITICAL)

def is_warning(log_level):
	return bool(log_level & WARNING)

def is_message(log_level):
	return bool(log_level & MESSAGE)

def is_info(log_level):
	return bool(log_level & INFO)

def is_debug(log_level):
	return bool(log_level & DEBUG)

def highest(log_level):
	if log_level < ERROR or is_error(log_level):
		highest = ERROR
	elif is_critical(log_level):
		highest = CRITICAL
	elif is_warning(log_level):
		highest = WARNING
	elif is_message(log_level):
		highest = MESSAGE
	elif is_info(log_level):
		highest = INFO
	else:
		highest = DEBUG

	return highest

def query(log_level):
	global last_queried_level
	last_queried_level = log_level

	return highest(log_level) <= output_level

def name(log_level=None):
	if log_level is None:
		log_level = last_queried_level

	return LEVELS_TO_NAMES[highest(log_level)] if log_level is not None else 'unknown'

def format(message, *args):
	msg = message % tuple(debug_str(arg) for arg in args)
	return "[%s] %s" % (name(), msg)

