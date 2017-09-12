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

import gettext
import math
import os.path
from gi.repository import GObject, Gtk, Gdk, GdkPixbuf, Gio, GtkSource, Gedit, PeasGtk
from xml.sax.saxutils import escape
from .utils import connect_handlers, disconnect_handlers

GETTEXT_PACKAGE = 'gedit-control-your-tabs'
BASE_PATH = os.path.dirname(os.path.realpath(__file__))
LOCALE_PATH = os.path.join(BASE_PATH, 'locale')

try:
	gettext.bindtextdomain(GETTEXT_PACKAGE, LOCALE_PATH)
	_ = lambda s: gettext.dgettext(GETTEXT_PACKAGE, s);
except:
	_ = lambda s: s


class ControlYourTabsPlugin(GObject.Object, Gedit.WindowActivatable, PeasGtk.Configurable):
	__gtype_name__ = 'ControlYourTabsPlugin'

	window = GObject.property(type=Gedit.Window)

	SELECTED_TAB_COLUMN = 3

	META_KEYS = ('Shift_L', 'Shift_R',
	             'Control_L', 'Control_R',
	             'Meta_L', 'Meta_R',
	             'Super_L', 'Super_R',
	             'Hyper_L', 'Hyper_R',
	             'Alt_L', 'Alt_R')
	             # Compose, Apple?

	MAX_TAB_WINDOW_ROWS = 9

	MAX_TAB_WINDOW_HEIGHT_PERCENTAGE = 0.5

	# based on MAX_DOC_NAME_LENGTH in gedit-documents-panel.c
	MAX_DOC_NAME_LENGTH = 60

	# based on formats in tab_get_name() in gedit-documents-panel.c < 3.12
	TAB_NAME_GEDITPANEL_FORMATS = {
		'modified': "<i>%s</i>",
		'readonly': " [<i>%s</i>]"
	}

	# based on formats in document_row_sync_tab_name_and_icon() in gedit-documents-panel.c >= 3.12
	TAB_NAME_LISTBOX_FORMATS = {
		'modified': "<b>%s</b>",
		'readonly': " [%s]"
	}

	# based on switch statement in _gedit_tab_get_icon() in gedit-tab.c < 3.12
	TAB_STATE_TO_STOCK_ICON = {
		Gedit.TabState.STATE_LOADING: Gtk.STOCK_OPEN,
		Gedit.TabState.STATE_REVERTING: Gtk.STOCK_REVERT_TO_SAVED,
		Gedit.TabState.STATE_SAVING: Gtk.STOCK_SAVE,
		Gedit.TabState.STATE_PRINTING: Gtk.STOCK_PRINT,
		Gedit.TabState.STATE_PRINT_PREVIEWING: Gtk.STOCK_PRINT_PREVIEW,
		Gedit.TabState.STATE_SHOWING_PRINT_PREVIEW: Gtk.STOCK_PRINT_PREVIEW,
		Gedit.TabState.STATE_LOADING_ERROR: Gtk.STOCK_DIALOG_ERROR,
		Gedit.TabState.STATE_REVERTING_ERROR: Gtk.STOCK_DIALOG_ERROR,
		Gedit.TabState.STATE_SAVING_ERROR: Gtk.STOCK_DIALOG_ERROR,
		Gedit.TabState.STATE_GENERIC_ERROR: Gtk.STOCK_DIALOG_ERROR,
		Gedit.TabState.STATE_EXTERNALLY_MODIFIED_NOTIFICATION: Gtk.STOCK_DIALOG_WARNING
	}

	# based on switch statement in _gedit_tab_get_icon() in gedit-tab.c >= 3.12
	TAB_STATE_TO_NAMED_ICON = {
		Gedit.TabState.STATE_PRINTING: 'printer-printing-symbolic',
		Gedit.TabState.STATE_PRINT_PREVIEWING: 'printer-symbolic',
		Gedit.TabState.STATE_SHOWING_PRINT_PREVIEW: 'printer-symbolic',
		Gedit.TabState.STATE_LOADING_ERROR: 'dialog-error-symbolic',
		Gedit.TabState.STATE_REVERTING_ERROR: 'dialog-error-symbolic',
		Gedit.TabState.STATE_SAVING_ERROR: 'dialog-error-symbolic',
		Gedit.TabState.STATE_GENERIC_ERROR: 'dialog-error-symbolic',
		Gedit.TabState.STATE_EXTERNALLY_MODIFIED_NOTIFICATION: 'dialog-warning-symbolic'
	}

	SETTINGS_SCHEMA_ID = 'com.thingsthemselves.gedit.plugins.controlyourtabs'

	USE_TABBAR_ORDER = 'use-tabbar-order'


	# gedit plugin api

	def __init__(self):
		GObject.Object.__init__(self)

	def do_activate(self):
		window = self.window
		notebooks = {}

		tabwin = Gtk.Window(type=Gtk.WindowType.POPUP)
		tabwin.set_transient_for(window)
		tabwin.set_destroy_with_parent(True)
		tabwin.set_accept_focus(False)
		tabwin.set_decorated(False)
		tabwin.set_resizable(False)
		tabwin.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
		tabwin.set_type_hint(Gdk.WindowTypeHint.UTILITY)
		tabwin.set_skip_taskbar_hint(False)
		tabwin.set_skip_pager_hint(False)

		sw = Gtk.ScrolledWindow()
		sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
		sw.show()

		tabwin.add(sw)

		view = Gtk.TreeView()
		view.set_enable_search(False)
		view.set_headers_visible(False)
		view.show()

		sw.add(view)

		col = Gtk.TreeViewColumn(_("Documents"))
		col.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)

		icon_cell = Gtk.CellRendererPixbuf()
		name_cell = Gtk.CellRendererText()
		space_cell = Gtk.CellRendererPixbuf()

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
		self._settings = self._get_settings()
		self._is_side_panel_stack = is_side_panel_stack

		tab = window.get_active_tab()
		if tab:
			self._setup(window, tab, notebooks, view)
			if self._multi:
				self.on_window_active_tab_changed(window, tab, notebooks, view)
		else:
			connect_handlers(self, window, ('tab-added',), 'window')

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
		self._is_side_panel_stack = None

	def do_update_state(self):
		pass


	# settings ui

	def do_create_configure_widget(self):
		settings = self._get_settings()
		if settings:
			widget = Gtk.CheckButton(_("Use tabbar order for Ctrl+Tab / Ctrl+Shift+Tab"))
			widget.set_active(settings.get_boolean(self.USE_TABBAR_ORDER))
			connect_handlers(self, widget, ('toggled',), 'configure_check_button', settings)
			connect_handlers(self, settings, ('changed::' + self.USE_TABBAR_ORDER,), 'configure_settings', widget)
		else:
			widget = Gtk.Box()
			widget.add(Gtk.Label(_("Sorry, no preferences are available for this version of gedit.")))
		widget.set_border_width(5)
		return widget

	def on_configure_check_button_toggled(self, widget, settings):
		settings.set_boolean(self.USE_TABBAR_ORDER, widget.get_active())

	def on_configure_settings_changed_use_tabbar_order(self, settings, prop, widget):
		widget.set_active(settings.get_boolean(self.USE_TABBAR_ORDER))


	# plugin setup

	def on_window_tab_added(self, window, tab):
		disconnect_handlers(self, window)
		self._setup(window, tab, self._notebooks, self._view)

	def _setup(self, window, tab, notebooks, view):
		if self._is_side_panel_stack:
			is_valid_size, icon_size_width, icon_size_height = Gtk.icon_size_lookup(Gtk.IconSize.MENU)
		else:
			is_valid_size, icon_size_width, icon_size_height = Gtk.icon_size_lookup_for_settings(tab.get_settings(), Gtk.IconSize.MENU)

		self._icon_cell.set_fixed_size(icon_size_height, icon_size_height)
		self._space_cell.set_fixed_size(icon_size_height, icon_size_height)

		multi = self._get_multi_notebook(tab)

		if multi:
			self._multi = multi

			for doc in window.get_documents():
				self.on_multi_notebook_notebook_added(multi, Gedit.Tab.get_from_document(doc).get_parent(), notebooks, view)

			connect_handlers(self, multi, ('notebook-added', 'notebook-removed', 'tab-added', 'tab-removed'), 'multi_notebook', notebooks, view)
			connect_handlers(self, window, ('tabs-reordered', 'active-tab-changed', 'key-press-event', 'key-release-event', 'focus-out-event', 'configure-event'), 'window', notebooks, view)

		else:
			try:
				Gedit.debug_plugin_message("cannot find multi notebook from %s", tab)
			except AttributeError:
				pass


	# signal handlers / main logic

	def on_multi_notebook_notebook_added(self, multi, notebook, notebooks, view):
		if notebook not in notebooks:
			model = Gtk.ListStore(GdkPixbuf.Pixbuf, str, Gedit.Tab, 'gboolean')
			connect_handlers(self, model, ('row-inserted', 'row-deleted', 'row-changed'), 'model', view, view.get_selection())
			notebooks[notebook] = [[], model]

			for tab in notebook.get_children():
				self.on_multi_notebook_tab_added(multi, notebook, tab, notebooks, view)

	def on_multi_notebook_notebook_removed(self, multi, notebook, notebooks, view):
		if notebook in notebooks:
			for tab in notebook.get_children():
				self.on_multi_notebook_tab_removed(multi, notebook, tab, notebooks, view)

			stack, model = notebooks[notebook]
			if view.get_model() == model:
				view.set_model(None)
			disconnect_handlers(self, model)
			del notebooks[notebook]

	def on_multi_notebook_tab_added(self, multi, notebook, tab, notebooks, view):
		stack, model = notebooks[notebook]
		if tab not in stack:
			stack.append(tab)
			model.append([self._get_tab_icon(tab), self._get_tab_name(tab), tab, False])
			connect_handlers(self, tab, ('notify::name', 'notify::state'), self.on_sync_icon_and_name, notebooks)

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

			if view.get_model() != model:
				view.set_model(model)
				self._schedule_tabwin_resize()

			for row in model:
				row[self.SELECTED_TAB_COLUMN] = False

			if not self._tabbing and not self._paging:
				if tab in stack:
					model.move_after(model.get_iter(stack.index(tab)), None)
					stack.remove(tab)
				else:
					model.insert(0, [self._get_tab_icon(tab), self._get_tab_name(tab), tab, False])

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
		is_tab_key = key in ('ISO_Left_Tab', 'Tab')
		is_page_key = key in ('Page_Up', 'Page_Down')
		is_up_dir = key in ('ISO_Left_Tab', 'Page_Up')

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
		if view.get_model() == model:
			self._schedule_tabwin_resize()

	def on_model_row_deleted(self, model, path, view, sel):
		if view.get_model() == model:
			self._schedule_tabwin_resize()

	def on_model_row_changed(self, model, path, iter, view, sel):
		if view.get_model() == model:
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
			model[path][0] = self._get_tab_icon(tab)
			model[path][1] = self._get_tab_name(tab)


	# tab name / icon

	# based on
	# <  3.12: tab_get_name() in gedit-documents-panel.c
	# >= 3.12: doc_get_name() and document_row_sync_tab_name_and_icon() in gedit-documents-panel.c
	def _get_tab_name(self, tab):
		doc = tab.get_document()
		name = doc.get_short_name_for_display()
		docname = Gedit.utils_str_middle_truncate(name, self.MAX_DOC_NAME_LENGTH)
		tab_name_formats = self.TAB_NAME_LISTBOX_FORMATS if self._is_side_panel_stack else self.TAB_NAME_GEDITPANEL_FORMATS

		if not doc.get_modified():
			tab_name = escape(docname)
		else:
			tab_name = tab_name_formats['modified'] % escape(docname)

		try:
			file = doc.get_file()
			is_readonly = GtkSource.File.is_readonly(file)
		except AttributeError:
			is_readonly = doc.get_readonly() # deprecated since 3.18

		if is_readonly:
			tab_name += tab_name_formats['readonly'] % escape(_("Read-Only"))

		return tab_name

	def _get_tab_icon(self, tab):
		if self._is_side_panel_stack:
			icon = self._get_named_tab_icon(tab)
		else:
			icon = self._get_stock_tab_icon(tab)
		return icon

	# based on _gedit_tab_get_icon() in gedit-tab.c >= 3.12
	def _get_named_tab_icon(self, tab):
		icon_name = None
		pixbuf = None
		state = tab.get_state()

		if state in self.TAB_STATE_TO_NAMED_ICON:
			icon_name = self.TAB_STATE_TO_NAMED_ICON[state]

		if icon_name:
			theme = Gtk.IconTheme.get_for_screen(tab.get_screen())
			is_valid_size, icon_size_width, icon_size_height = Gtk.icon_size_lookup(Gtk.IconSize.MENU)
			pixbuf = Gtk.IconTheme.load_icon(theme, icon_name, icon_size_height, 0)

		return pixbuf

	# based on _gedit_tab_get_icon() in gedit-tab.c < 3.12
	def _get_stock_tab_icon(self, tab):
		theme = Gtk.IconTheme.get_for_screen(tab.get_screen())
		is_valid_size, icon_size_width, icon_size_height = Gtk.icon_size_lookup_for_settings(tab.get_settings(), Gtk.IconSize.MENU)
		state = tab.get_state()

		if state in self.TAB_STATE_TO_STOCK_ICON:
			try:
				pixbuf = self._get_stock_icon(theme, self.TAB_STATE_TO_STOCK_ICON[state], icon_size_height)
			except GObject.GError:
				pixbuf = None
		else:
			pixbuf = None

		if not pixbuf:
			pixbuf = self._get_icon(theme, tab.get_document().get_location(), icon_size_height)

		return pixbuf

	# based on get_stock_icon() in gedit-tab.c in < 3.12
	def _get_stock_icon(self, theme, stock, size):
		pixbuf = theme.load_icon(stock, size, 0)
		return self._resize_icon(pixbuf, size)

	# based on get_icon() in gedit-tab.c in < 3.12
	def _get_icon(self, theme, location, size):
		if not location:
			return self._get_stock_icon(theme, Gtk.STOCK_FILE, size)

		# FIXME: Doing a sync stat is bad, this should be fixed
		try:
			info = location.query_info(Gio.FILE_ATTRIBUTE_STANDARD_ICON, Gio.FileQueryInfoFlags.NONE, None)
		except GObject.GError:
			info = None

		if not info:
			return self._get_stock_icon(theme, Gtk.STOCK_FILE, size)

		icon = info.get_icon()

		if not icon:
			return self._get_stock_icon(theme, Gtk.STOCK_FILE, size)

		icon_info = theme.lookup_by_gicon(icon, size, 0);

		if not icon_info:
			return self._get_stock_icon(theme, Gtk.STOCK_FILE, size)

		pixbuf = icon_info.load_icon()

		if not pixbuf:
			return self._get_stock_icon(theme, Gtk.STOCK_FILE, size)

		return self._resize_icon(pixbuf, size)

	# based on resize_icon() in gedit-tab.c in < 3.12
	def _resize_icon(self, pixbuf, size):
		width = pixbuf.get_width()
		height = pixbuf.get_height()

		# if the icon is larger than the nominal size, scale down
		if max(width, height) > size:
			if width > height:
				height = height * size / width
				width = size
			else:
				width = width * size / height
				height = size

			pixbuf = pixbuf.scale_simple(width, height, GdkPixbuf.InterpType.BILINEAR)

		return pixbuf


	# tab window resizing

	def _schedule_tabwin_resize(self):
		if not self._tabwin_resize_id:
			# need to wait a little before asking the treeview for its preferred size
			# maybe because treeview rendering is async?
			# this feels like a giant hack
			self._tabwin_resize_id = GObject.idle_add(self._do_tabwin_resize)

	def _cancel_tabwin_resize(self):
		if self._tabwin_resize_id:
			GObject.source_remove(self._tabwin_resize_id)
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


	# misc

	# this is a /hack/
	def _get_multi_notebook(self, tab):
		multi = tab.get_parent()
		while multi:
			if multi.__gtype__.name == 'GeditMultiNotebook':
				break
			multi = multi.get_parent()
		return multi

	def _get_settings(self):
		schemas_path = os.path.join(BASE_PATH, 'schemas')
		try:
			# available in gedit >= 3.4
			schema_source = Gio.SettingsSchemaSource.new_from_directory(schemas_path, Gio.SettingsSchemaSource.get_default(), False)
			schema = Gio.SettingsSchemaSource.lookup(schema_source, self.SETTINGS_SCHEMA_ID, False)
			settings = Gio.Settings.new_full(schema, None, None) if schema else None
		except AttributeError:
			settings = None
		except:
			try:
				Gedit.debug_plugin_message("could not load settings schema from %s", schemas_path)
			except AttributeError:
				pass
			settings = None
		return settings
