# -*- coding: utf-8 -*-
#
# plugin.py
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
gi.require_version('GLib', '2.0')
gi.require_version('Peas', '1.0')

import os.path
from gi.repository import GLib, Peas


data_dir = Peas.Engine.get_default().get_plugin_info('controlyourtabs').get_data_dir()

try:
	import locale
	locale.bindtextdomain('gedit-control-your-tabs', os.path.join(data_dir, 'locale'))
	locale.bind_textdomain_codeset('gedit-control-your-tabs', 'UTF-8')
except:
	pass

_ = lambda s: GLib.dgettext('gedit-control-your-tabs', s)

