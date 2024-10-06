# -*- coding: utf-8 -*-
#
# editor.py
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
import inspect
import os


# based on get_trace_info() in Gedit.py
def get_trace_info(num_back_frames=0):
	frame = inspect.currentframe().f_back
	try:
		for i in range(num_back_frames):
			back_frame = frame.f_back
			if back_frame is None:
				break
			frame = back_frame

		filename = frame.f_code.co_filename

		# http://code.activestate.com/recipes/145297-grabbing-the-current-line-number-easily/
		lineno = frame.f_lineno

		func_name = frame.f_code.co_name
		try:
			# http://stackoverflow.com/questions/2203424/python-how-to-retrieve-class-information-from-a-frame-object
			cls_name = frame.f_locals["self"].__class__.__name__
		except:
			pass
		else:
			func_name = "%s.%s" % (cls_name, func_name)

		return (filename, lineno, func_name)
	finally:
		frame = None

# based on debug_plugin_message() in Gedit.py and gedit-debug.c
def _debug_plugin_message(format, *format_args):
	filename, lineno, func_name = get_trace_info(1)
	message = format % format_args
	print("%s:%d (%s) %s" % (filename, lineno, func_name, message), flush=True)

try:
	gi.require_version('Gedit', '3.0')
except ValueError:
	Editor = None
else:
	from gi.repository import Gedit as Editor
	name = 'gedit'
	use_new_tab_name_style = True
	use_symbolic_icons = True
	use_document_icons = False

if not Editor:
	try:
		gi.require_version('Xed', '1.0')
	except ValueError:
		Editor = None
	else:
		from gi.repository import Xed as Editor
		name = 'xed'
		use_new_tab_name_style = False
		use_symbolic_icons = True
		use_document_icons = True

if not Editor:
	try:
		# needs to be last because Pluma is a non-private namespace
		gi.require_version('Pluma', '1.0')
	except ValueError:
		Editor = None
	else:
		from gi.repository import Pluma as Editor
		name = 'Pluma'
		use_new_tab_name_style = False
		use_symbolic_icons = False
		use_document_icons = True

try:
	debug_plugin_message = Editor.debug_plugin_message
except AttributeError:
	debug_plugin_message = lambda *args: None

	is_debug = os.getenv('%s_DEBUG' % name.upper())
	is_debug_plugins = os.getenv('%s_DEBUG_PLUGINS' % name.upper())

	if is_debug or is_debug_plugins:
		debug_plugin_message = _debug_plugin_message

