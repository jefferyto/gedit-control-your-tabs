# -*- coding: utf-8 -*-
#
# __init__.py
# This file is part of Control Your Tabs, a plugin for gedit
#
# Copyright (C) 2010-2014, 2016-2017 Jeffery To <jeffery.to@gmail.com>
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
gi.require_version('Gedit', '3.0')

import math
import os.path
from gi.repository import GObject, GLib, Gtk, Gdk, GdkPixbuf, Gio, Gedit, PeasGtk
from .utils import connect_handlers, disconnect_handlers
from . import tabinfo, tabinfo_pre312

BASE_PATH = os.path.dirname(os.path.realpath(__file__))
LOCALE_PATH = os.path.join(BASE_PATH, 'locale')

try:
	import gettext
	gettext.bindtextdomain('gedit-control-your-tabs', LOCALE_PATH)
	gettext.textdomain('gedit-control-your-tabs')
	_ = gettext.gettext
except:
	_ = lambda s: s


class ControlYourTabsPlugin(GObject.Object, Gedit.WindowActivatable):
	__gtype_name__ = 'ControlYourTabsPlugin'

	window = GObject.property(type=Gedit.Window)

	SELECTED_TAB_COLUMN = 3

	META_KEYS = ['Shift_L', 'Shift_R',
	             'Control_L', 'Control_R',
	             'Meta_L', 'Meta_R',
	             'Super_L', 'Super_R',
	             'Hyper_L', 'Hyper_R',
	             'Alt_L', 'Alt_R']
	             # Compose, Apple?

	MAX_TAB_WINDOW_ROWS = 9

	MAX_TAB_WINDOW_HEIGHT_PERCENTAGE = 0.5

	USE_TABBAR_ORDER = 'use-tabbar-order'


	# gedit plugin api

	def __init__(self):
		GObject.Object.__init__(self)

	def do_activate(self):
		window = self.window
		notebooks = {}

		tabwin = Gtk.Window.new(Gtk.WindowType.POPUP)
		tabwin.set_transient_for(window)
		tabwin.set_destroy_with_parent(True)
		tabwin.set_accept_focus(False)
		tabwin.set_decorated(False)
		tabwin.set_resizable(False)
		tabwin.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
		tabwin.set_type_hint(Gdk.WindowTypeHint.UTILITY)
		tabwin.set_skip_taskbar_hint(False)
		tabwin.set_skip_pager_hint(False)

		sw = Gtk.ScrolledWindow.new(None, None)
		sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
		sw.show()

		tabwin.add(sw)

		view = Gtk.TreeView.new()
		view.set_enable_search(False)
		view.set_headers_visible(False)
		view.show()

		sw.add(view)

		col = Gtk.TreeViewColumn.new()
		col.set_title(_("Documents"))
		col.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)

		icon_cell = Gtk.CellRendererPixbuf.new()
		name_cell = Gtk.CellRendererText.new()
		space_cell = Gtk.CellRendererPixbuf.new()

		col.pack_start(icon_cell, False)
		col.pack_start(name_cell, True)
		col.pack_start(space_cell, False)

		col.add_attribute(icon_cell, 'pixbuf', 0)
		col.add_attribute(name_cell, 'markup', 1)

		view.append_column(col)

		sel = view.get_selection()
		sel.set_mode(Gtk.SelectionMode.SINGLE)

		# hack to ensure tabwin is correctly positioned/sized on first show
		view.realize()

		try:
			GtkStack = Gtk.Stack
		except AttributeError:
			is_side_panel_stack = False
		else:
			is_side_panel_stack = isinstance(window.get_side_panel(), GtkStack) # since 3.12

		self._tabbing = False
		self._paging = False
		self._switching = False
		self._ctrl_l = False
		self._ctrl_r = False
		self._multi = None
		self._notebooks = notebooks
		self._tabwin = tabwin
		self._view = view
		self._sw = sw
		self._icon_cell = icon_cell
		self._space_cell = space_cell
		self._tabwin_resize_id = None
		self._settings = get_settings()
		self._tabinfo = tabinfo if is_side_panel_stack else tabinfo_pre312

		tab = window.get_active_tab()
		if tab:
			self._setup(window, tab, notebooks, view)
			if self._multi:
				self.on_window_active_tab_changed(window, tab, notebooks, view)
		else:
			connect_handlers(self, window, ['tab-added'], 'window')

	def do_deactivate(self):
		window = self.window

		disconnect_handlers(self, window)

		if self._multi:
			disconnect_handlers(self, self._multi)

		notebooks = self._notebooks
		for notebook in notebooks:
			disconnect_handlers(self, notebooks[notebook][1])

		for doc in window.get_documents():
			disconnect_handlers(self, Gedit.Tab.get_from_document(doc))

		self._cancel_tabwin_resize()
		self._end_switching()

		self._tabwin.destroy()

		self._tabbing = None
		self._paging = None
		self._switching = None
		self._ctrl_l = None
		self._ctrl_r = None
		self._multi = None
		self._notebooks = None
		self._tabwin = None
		self._view = None
		self._sw = None
		self._icon_cell = None
		self._space_cell = None
		self._tabwin_resize_id = None
		self._settings = None
		self._tabinfo = None

	def do_update_state(self):
		pass


	# plugin setup

	def on_window_tab_added(self, window, tab):
		disconnect_handlers(self, window)
		self._setup(window, tab, self._notebooks, self._view)

	def _setup(self, window, tab, notebooks, view):
		icon_size = self._tabinfo.get_tab_icon_size(tab)

		self._icon_cell.set_fixed_size(icon_size, icon_size)
		self._space_cell.set_fixed_size(icon_size, icon_size)

		multi = get_multi_notebook(tab)

		if multi:
			self._multi = multi

			for doc in window.get_documents():
				self.on_multi_notebook_notebook_added(multi, Gedit.Tab.get_from_document(doc).get_parent(), notebooks, view)

			connect_handlers(self, multi, ['notebook-added', 'notebook-removed', 'tab-added', 'tab-removed'], 'multi_notebook', notebooks, view)
			connect_handlers(self, window, ['tabs-reordered', 'active-tab-changed', 'key-press-event', 'key-release-event', 'focus-out-event', 'configure-event'], 'window', notebooks, view)

		else:
			try:
				Gedit.debug_plugin_message("cannot find multi notebook from %s", tab)
			except AttributeError:
				pass


	# signal handlers / main logic

	def on_multi_notebook_notebook_added(self, multi, notebook, notebooks, view):
		if notebook not in notebooks:
			model = Gtk.ListStore.new([GdkPixbuf.Pixbuf, str, Gedit.Tab, bool])
			connect_handlers(self, model, ['row-inserted', 'row-deleted', 'row-changed'], 'model', view, view.get_selection())
			notebooks[notebook] = ([], model)

			for tab in notebook.get_children():
				self.on_multi_notebook_tab_added(multi, notebook, tab, notebooks, view)

	def on_multi_notebook_notebook_removed(self, multi, notebook, notebooks, view):
		if notebook in notebooks:
			for tab in notebook.get_children():
				self.on_multi_notebook_tab_removed(multi, notebook, tab, notebooks, view)

			stack, model = notebooks[notebook]
			if view.get_model() is model:
				view.set_model(None)
			disconnect_handlers(self, model)
			del notebooks[notebook]

	def on_multi_notebook_tab_added(self, multi, notebook, tab, notebooks, view):
		stack, model = notebooks[notebook]
		if tab not in stack:
			stack.append(tab)
			model.append((self._tabinfo.get_tab_icon(tab), self._tabinfo.get_tab_name(tab), tab, False))
			connect_handlers(self, tab, ['notify::name', 'notify::state'], self.on_sync_icon_and_name, notebooks)

	def on_multi_notebook_tab_removed(self, multi, notebook, tab, notebooks, view):
		stack, model = notebooks[notebook]
		if tab in stack:
			disconnect_handlers(self, tab)
			model.remove(model.get_iter(stack.index(tab)))
			stack.remove(tab)

	def on_window_tabs_reordered(self, window, notebooks, view):
		multi = self._multi
		tab = window.get_active_tab()
		new_notebook = tab.get_parent()
		if tab not in notebooks[new_notebook][0]:
			old_notebook = None
			for notebook in notebooks:
				if tab in notebooks[notebook][0]:
					old_notebook = notebook
					break
			if old_notebook:
				self.on_multi_notebook_tab_removed(multi, old_notebook, tab, notebooks, view)
			self.on_multi_notebook_tab_added(multi, new_notebook, tab, notebooks, view)

	def on_window_active_tab_changed(self, window, tab, notebooks, view):
		if not self._switching:
			stack, model = notebooks[tab.get_parent()]

			if view.get_model() is not model:
				view.set_model(model)
				self._schedule_tabwin_resize()

			for row in model:
				row[self.SELECTED_TAB_COLUMN] = False

			if not self._tabbing and not self._paging:
				if tab in stack:
					model.move_after(model.get_iter(stack.index(tab)), None)
					stack.remove(tab)
				else:
					model.insert(0, (self._tabinfo.get_tab_icon(tab), self._tabinfo.get_tab_name(tab), tab, False))

				stack.insert(0, tab)
				model[0][self.SELECTED_TAB_COLUMN] = True

			else:
				model[stack.index(tab)][self.SELECTED_TAB_COLUMN] = True

	def on_window_key_press_event(self, window, event, notebooks, view):
		key = Gdk.keyval_name(event.keyval)
		state = event.state & Gtk.accelerator_get_default_mod_mask()

		if key == 'Control_L':
			self._ctrl_l = True

		if key == 'Control_R':
			self._ctrl_r = True

		if key in self.META_KEYS or not state & Gdk.ModifierType.CONTROL_MASK:
			return False

		is_ctrl = state == Gdk.ModifierType.CONTROL_MASK
		is_ctrl_shift = state == Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.SHIFT_MASK
		is_tab_key = key in ['ISO_Left_Tab', 'Tab']
		is_page_key = key in ['Page_Up', 'Page_Down']
		is_up_dir = key in ['ISO_Left_Tab', 'Page_Up']

		if not (((is_ctrl or is_ctrl_shift) and is_tab_key) or (is_ctrl and is_page_key)):
			self._end_switching()
			return False

		cur = window.get_active_tab()
		if cur:
			settings = self._settings
			notebook = cur.get_parent()
			stack, model = notebooks[notebook]
			is_tabbing = is_tab_key and not (settings and settings.get_boolean(self.USE_TABBAR_ORDER))
			tabs = stack if is_tabbing else notebook.get_children()
			tlen = len(tabs)

			if tlen > 1 and cur in tabs:
				i = -1 if is_up_dir else 1
				next = tabs[(tabs.index(cur) + i) % tlen]

				model[stack.index(cur)][self.SELECTED_TAB_COLUMN] = False
				model[stack.index(next)][self.SELECTED_TAB_COLUMN] = True

				if is_tabbing:
					tabwin = self._tabwin

					if not self._tabbing:
						view.scroll_to_cell(Gtk.TreePath.new_first(), None, True, 0, 0)
						tabwin.show_all()
					else:
						tabwin.present_with_time(event.time)

					self._tabbing = True
				else:
					self._paging = True

				self._switching = True
				window.set_active_tab(next)
				self._switching = False

		return True

	def on_window_key_release_event(self, window, event, notebooks, view):
		key = Gdk.keyval_name(event.keyval)

		if key == 'Control_L':
			self._ctrl_l = False

		if key == 'Control_R':
			self._ctrl_r = False

		if not self._ctrl_l and not self._ctrl_r:
			self._end_switching()

	def on_window_focus_out_event(self, window, event, notebooks, view):
		self._end_switching()

	def on_window_configure_event(self, window, event, notebooks, view):
		self._schedule_tabwin_resize()

	def _end_switching(self):
		if self._tabbing or self._paging:
			self._tabbing = False
			self._paging = False
			self._switching = False
			self._ctrl_l = False
			self._ctrl_r = False
			self._tabwin.hide()

			window = self.window
			tab = window.get_active_tab()
			if tab:
				self.on_window_active_tab_changed(window, tab, self._notebooks, self._view)

	def on_model_row_inserted(self, model, path, iter, view, sel):
		if view.get_model() is model:
			self._schedule_tabwin_resize()

	def on_model_row_deleted(self, model, path, view, sel):
		if view.get_model() is model:
			self._schedule_tabwin_resize()

	def on_model_row_changed(self, model, path, iter, view, sel):
		if view.get_model() is model:
			if model[path][self.SELECTED_TAB_COLUMN]:
				sel.select_path(path)
				view.scroll_to_cell(path, None, True, 0.5, 0)
			else:
				sel.unselect_path(path)
			self._schedule_tabwin_resize()

	def on_sync_icon_and_name(self, tab, pspec, notebooks):
		stack, model = notebooks[tab.get_parent()]
		if tab in stack:
			path = stack.index(tab)
			model[path][0] = self._tabinfo.get_tab_icon(tab)
			model[path][1] = self._tabinfo.get_tab_name(tab)


	# tab window resizing

	def _schedule_tabwin_resize(self):
		if not self._tabwin_resize_id:
			# need to wait a little before asking the treeview for its preferred size
			# maybe because treeview rendering is async?
			# this feels like a giant hack
			try:
				resize_id = GLib.idle_add(self._do_tabwin_resize)
			except TypeError:
				# gedit 3.0
				resize_id = GObject.idle_add(self._do_tabwin_resize)

			self._tabwin_resize_id = resize_id

	def _cancel_tabwin_resize(self):
		if self._tabwin_resize_id:
			GLib.source_remove(self._tabwin_resize_id)
			self._tabwin_resize_id = None

	def _do_tabwin_resize(self):
		view = self._view
		sw = self._sw

		view_min_size, view_nat_size = view.get_preferred_size()
		view_height = max(view_min_size.height, view_nat_size.height)

		num_rows = max(len(view.get_model()), 2)
		row_height = math.ceil(view_height / num_rows)
		max_rows_height = self.MAX_TAB_WINDOW_ROWS * row_height

		win_width, win_height = self.window.get_size()
		max_win_height = round(self.MAX_TAB_WINDOW_HEIGHT_PERCENTAGE * win_height)

		max_height = min(max_rows_height, max_win_height)

		# we can't reliably tell if overlay scrolling is being used
		# since gtk_scrolled_window_get_overlay_scrolling() can still return True if GTK_OVERLAY_SCROLLING=0 is set
		# and even if we can tell if overlay scrolling is disabled,
		# we cannot tell if the scrolled window has reserved enough space for the scrollbar
		#   fedora < 25: reserved
		#   fedora >= 25: not reserved
		#   ubuntu 17.04: reserved
		# so let's ignore overlay scrolling for now :-(

		vscrollbar_policy = Gtk.PolicyType.AUTOMATIC if view_height > max_height else Gtk.PolicyType.NEVER
		sw.set_policy(Gtk.PolicyType.NEVER, vscrollbar_policy)

		sw_min_size, sw_nat_size = sw.get_preferred_size()

		tabwin_width = max(sw_min_size.width, sw_nat_size.width)
		tabwin_height = min(view_height, max_height)

		self._tabwin.set_size_request(tabwin_width, tabwin_height)

		self._tabwin_resize_id = None
		return False


class ControlYourTabsConfigurable(GObject.Object, PeasGtk.Configurable):

	__gtype_name__ = 'ControlYourTabsConfigurable'


	def do_create_configure_widget(self):
		settings = get_settings()

		if settings:
			widget = Gtk.CheckButton.new_with_label(
				_("Use tabbar order for Ctrl+Tab / Ctrl+Shift+Tab")
			)

			settings.bind(
				'use-tabbar-order',
				widget, 'active',
				Gio.SettingsBindFlags.DEFAULT
			)

		else:
			label = Gtk.Label.new(
				_("Sorry, no preferences are available for this version of gedit.")
			)

			widget = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
			widget.add(label)

		widget.set_border_width(5)

		widget._settings = settings

		return widget


# this is a /hack/
# can do window.get_template_child(Gedit.Window, 'multi_notebook') since 3.12
def get_multi_notebook(tab):
	multi = tab.get_parent()

	while multi:
		if multi.__gtype__.name == 'GeditMultiNotebook':
			break

		multi = multi.get_parent()

	return multi

def get_settings():
	schemas_path = os.path.join(BASE_PATH, 'schemas')

	try:
		schema_source = Gio.SettingsSchemaSource.new_from_directory(
			schemas_path,
			Gio.SettingsSchemaSource.get_default(),
			False
		)
	except AttributeError: # gedit < 3.4
		try:
			Gedit.debug_plugin_message("relocatable schemas not supported")
		except AttributeError:
			pass

		schema_source = None

	except:
		try:
			Gedit.debug_plugin_message("could not load settings schema source from %s", schemas_path)
		except AttributeError:
			pass

		schema_source = None

	if not schema_source:
		return None

	schema = schema_source.lookup(
		'com.thingsthemselves.gedit.plugins.controlyourtabs',
		False
	)

	if not schema:
		return None

	return Gio.Settings.new_full(
		schema,
		None,
		'/com/thingsthemselves/gedit/plugins/controlyourtabs/'
	)

