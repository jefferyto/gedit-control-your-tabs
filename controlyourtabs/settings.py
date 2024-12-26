# -*- coding: utf-8 -*-
#
# settings.py
# This file is part of Control Your Tabs, a plugin for gedit/Pluma/xed
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
gi.require_version('Gio', '2.0')

import os.path
from gi.repository import Gio
from .plugin import data_dir as plugin_data_dir
from . import editor, log


def get_settings():
	if log.query(log.DEBUG):
		editor.debug_plugin_message(log.format(""))

	schemas_directory = os.path.join(plugin_data_dir, 'schemas')
	default_schema_source = Gio.SettingsSchemaSource.get_default()
	schema_id = 'com.thingsthemselves.%s.plugins.controlyourtabs' % editor.name.lower()

	try:
		schema_source = Gio.SettingsSchemaSource.new_from_directory(
			schemas_directory,
			default_schema_source,
			False
		)

	except:
		if log.query(log.INFO):
			editor.debug_plugin_message(log.format("Could not load schema source from %s", schemas_directory))

		schema_source = None

	if not schema_source:
		schema_source = default_schema_source

	schema = schema_source.lookup(schema_id, True) if schema_source else None
	return Gio.Settings.new_full(schema, None, None) if schema else None

