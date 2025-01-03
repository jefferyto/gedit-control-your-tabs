# -*- coding: utf-8 -*-
#
# configurable.py
# This file is part of Control Your Tabs, a plugin for gedit/Pluma/xed
#
# Copyright (C) 2010-2013, 2017-2018, 2020, 2023-2024 Jeffery To <jeffery.to@gmail.com>
# https://github.com/jefferyto/gedit-control-your-tabs
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.

import gi
gi.require_version('GObject', '2.0')
gi.require_version('Gio', '2.0')
gi.require_version('Gtk', '3.0')
gi.require_version('PeasGtk', '1.0')

from gi.repository import GObject, Gio, Gtk, PeasGtk
from .plugin import _
from .settings import get_settings
from . import editor, log


class ControlYourTabsConfigurable(GObject.Object, PeasGtk.Configurable):

	__gtype_name__ = 'ControlYourTabsConfigurable'


	def do_create_configure_widget(self):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format(""))

		settings = get_settings()

		if settings:
			if log.query(log.INFO):
				editor.debug_plugin_message(log.format("Loaded settings"))

			widget = Gtk.CheckButton.new_with_label(
				_("Ctrl+Tab and Ctrl+Shift+Tab switch to tabs on the left and right")
			)

			settings.bind(
				'use-tabbar-order',
				widget, 'active',
				Gio.SettingsBindFlags.DEFAULT
			)

			widget._settings = settings

		else:
			if log.query(log.WARNING):
				editor.debug_plugin_message(log.format("Could not load settings"))

			widget = Gtk.Label.new(
				_("Unable to load preferences")
			)

		box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
		box.set_margin_start(12)
		box.set_margin_end(12)
		box.set_margin_top(12)
		box.set_margin_bottom(12)
		box.add(widget)

		return box

