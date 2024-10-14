# -*- coding: utf-8 -*-
#
# tabmodel.py
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
gi.require_version('GObject', '2.0')
gi.require_version('GdkPixbuf', '2.0')
gi.require_version('Gtk', '3.0')

from functools import wraps
from gi.repository import GObject, GdkPixbuf, Gtk
from .utils import connect_handlers
from . import editor, log, tabinfo


class ControlYourTabsTabModel(GObject.Object):

	__gtype_name__ = 'ControlYourTabsTabModel'

	__gsignals__ = { # before pygobject 3.4
		'row-inserted': (GObject.SignalFlags.RUN_FIRST, None, (Gtk.TreePath,)),
		'row-deleted': (GObject.SignalFlags.RUN_FIRST, None, (Gtk.TreePath,)),
		'row-changed': (GObject.SignalFlags.RUN_FIRST, None, (Gtk.TreePath,)),
		'rows-reordered': (GObject.SignalFlags.RUN_FIRST, None, ()),
		'selected-path-changed': (GObject.SignalFlags.RUN_FIRST, None, (Gtk.TreePath,))
	}


	def _model_modifier(fn):
		@wraps(fn)
		def wrapper(self, *args, **kwargs):
			prev_path = self.get_selected_path()

			result = fn(self, *args, **kwargs)

			cur_path = self.get_selected_path()

			if cur_path != prev_path:
				self.emit('selected-path-changed', cur_path)

			return result

		return wrapper


	def __init__(self):
		GObject.Object.__init__(self)

		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s", self))

		self._model = Gtk.ListStore.new((GdkPixbuf.Pixbuf, str, editor.Editor.Tab))
		self._references = {}
		self._selected = None

		connect_handlers(
			self, self._model,
			[
				'row-inserted',
				'row-deleted',
				'row-changed',
				'rows-reordered'
			],
			'model'
		)

	def __len__(self):
		return len(self._model)

	def __getitem__(self, key):
		return self._model[key][2]

	@_model_modifier
	def __delitem__(self, key):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s, key=%s", self, key))

		tab = self._model[key][2]

		if self._selected is tab:
			self._selected = None

		del self._references[tab]

		# before pygobject 3.2, cannot del model[path]
		self._model.remove(self._model.get_iter(key))

	def __iter__(self):
		return [row[2] for row in self._model]

	def __contains__(self, item):
		return item in self._references

	@property
	def model(self):
		return self._model

	def on_model_row_inserted(self, model, path, iter_):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s, %s, path=%s", self, model, path))

		self.emit('row-inserted', path)

	def on_model_row_deleted(self, model, path):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s, %s, path=%s", self, model, path))

		self.emit('row-deleted', path)

	def on_model_row_changed(self, model, path, iter_):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s, %s, path=%s", self, model, path))

		self.emit('row-changed', path)

	def on_model_rows_reordered(self, model, path, iter_, new_order):
		if log.query(log.DEBUG):
			# path is suppose to point to the parent node of the reordered rows
			# if top level rows are reordered, path is invalid (null?)
			# so don't print it out here, because will throw an error
			editor.debug_plugin_message(log.format("%s, %s", self, model))

		self.emit('rows-reordered')

	def do_row_inserted(self, path):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s, path=%s", self, path))

	def do_row_deleted(self, path):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s, path=%s", self, path))

	def do_row_changed(self, path):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s, path=%s", self, path))

	def do_rows_reordered(self):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s", self))

	def do_selected_path_changed(self, path):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s, path=%s", self, path))

	@_model_modifier
	def insert(self, position, tab):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s, position=%s, %s", self, position, tab))

		tab_iter = self._model.insert(
			position,
			(
				tabinfo.get_tab_icon(tab),
				tabinfo.get_tab_name(tab),
				tab
			)
		)

		self._references[tab] = Gtk.TreeRowReference.new(self._model, self._model.get_path(tab_iter))

	def append(self, tab):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s, %s", self, tab))

		self.insert(len(self._model), tab) # before pygobject 3.2, -1 position does not work

	def prepend(self, tab):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s, %s", self, tab))

		self.insert(0, tab)

	def remove(self, tab):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s, %s", self, tab))

		del self[self.get_path(tab)]

	@_model_modifier
	def move(self, tab, sibling, move_before):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s, %s, %s, move_before=%s", self, tab, sibling, move_before))

		tab_iter = self._get_iter(tab)
		sibling_iter = self._get_iter(sibling) if sibling else None

		if move_before:
			self._model.move_before(tab_iter, sibling_iter)
		else:
			self._model.move_after(tab_iter, sibling_iter)

	def move_before(self, tab, sibling=None):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s, %s, %s", self, tab, sibling))

		self.move(tab, sibling, True)

	def move_after(self, tab, sibling=None):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s, %s, %s", self, tab, sibling))

		self.move(tab, sibling, False)

	def get_path(self, tab):
		return self._references[tab].get_path()

	def index(self, tab):
		return int(str(self.get_path(tab)))

	def _get_iter(self, tab):
		return self._model.get_iter(self.get_path(tab))

	@_model_modifier
	def select(self, tab):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s, %s", self, tab))

		self._selected = tab

	def unselect(self):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s", self))

		self.select(None)

	def get_selected(self):
		return self._selected

	def get_selected_path(self):
		return self.get_path(self._selected) if self._selected else None

	def update(self, tab):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s, %s", self, tab))

		path = self.get_path(tab)

		self._model[path][0] = tabinfo.get_tab_icon(tab)
		self._model[path][1] = tabinfo.get_tab_name(tab)

