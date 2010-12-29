# -*- coding: utf-8 -*-
#
# Control Your Tabs, a plugin for gedit
# Switch between tabs using Ctrl-Tab / Ctrl-Shift-Tab and
# Ctrl-PageUp / Ctrl-PageDown
# v0.1.2
#
# Ctrl-Tab / Ctrl-Shift-Tab switch tabs in most recently used order.
# Ctrl-PageUp / Ctrl-PageDown switch tabs in tabbar order.
#
# Inspired by:
#     TabSwitch by Elia Sarti
#     TabPgUpPgDown by Eran M.
#     the gEdit Documents panel
#
# Copyright (C) 2010 Jeffery To <jeffery.to@gmail.com>
# http://www.thingsthemselves.com/gedit/
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

import gedit
import glib
import gtk
import gio
from gettext import gettext as _
from xml.sax.saxutils import escape

class ControlYourTabsWindowHelper:
	HANDLER_IDS = 'ControlYourTabsPluginHandlerIds'

	SELECTED_TAB_COLUMN = 3

	META_KEYS = ('Shift_L', 'Shift_R',
	             'Control_L', 'Control_R',
	             'Meta_L', 'Meta_R',
	             'Super_L', 'Super_R',
	             'Hyper_L', 'Hyper_R',
	             'Alt_L', 'Alt_R')
	             # Compose, Apple?

	MAX_DOC_NAME_LENGTH = 60

	MAX_TAB_WINDOW_HEIGHT = 250

	TAB_STATE_TO_ICON = {
		gedit.TAB_STATE_LOADING: gtk.STOCK_OPEN,
		gedit.TAB_STATE_REVERTING: gtk.STOCK_REVERT_TO_SAVED,
		gedit.TAB_STATE_SAVING: gtk.STOCK_SAVE,
		gedit.TAB_STATE_PRINTING: gtk.STOCK_PRINT,
		gedit.TAB_STATE_PRINT_PREVIEWING: gtk.STOCK_PRINT_PREVIEW,
		gedit.TAB_STATE_SHOWING_PRINT_PREVIEW: gtk.STOCK_PRINT_PREVIEW,
		gedit.TAB_STATE_LOADING_ERROR: gtk.STOCK_DIALOG_ERROR,
		gedit.TAB_STATE_REVERTING_ERROR: gtk.STOCK_DIALOG_ERROR,
		gedit.TAB_STATE_SAVING_ERROR: gtk.STOCK_DIALOG_ERROR,
		gedit.TAB_STATE_GENERIC_ERROR: gtk.STOCK_DIALOG_ERROR,
		gedit.TAB_STATE_EXTERNALLY_MODIFIED_NOTIFICATION: gtk.STOCK_DIALOG_WARNING
	}

	def __init__(self, plugin, window):
		stack = []

		tabwin = gtk.Window(gtk.WINDOW_POPUP)
		tabwin.set_transient_for(window)
		tabwin.set_destroy_with_parent(True)
		tabwin.set_accept_focus(False)
		tabwin.set_decorated(False)
		tabwin.set_resizable(False)
		tabwin.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
		tabwin.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_UTILITY)
		tabwin.set_skip_taskbar_hint(False)
		tabwin.set_skip_pager_hint(False)

		sw = gtk.ScrolledWindow()
		sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
		sw.show()

		tabwin.add(sw)

		model = gtk.ListStore(gtk.gdk.Pixbuf, str, gedit.Tab, 'gboolean')

		view = gtk.TreeView(model)
		view.set_enable_search(False)
		view.set_headers_visible(False)
		view.show()

		sw.add(view)

		col = gtk.TreeViewColumn(_('Documents'))
		col.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
		cell = gtk.CellRendererPixbuf()
		col.pack_start(cell, False)
		col.add_attribute(cell, 'pixbuf', 0)
		cell = gtk.CellRendererText()
		col.pack_start(cell, True)
		col.add_attribute(cell, 'markup', 1)

		view.append_column(col)

		sel = view.get_selection()
		sel.set_mode(gtk.SELECTION_SINGLE)

		self.connect_handlers(model, ('row-changed',), 'model', view, sel)

		self._tabbing = False
		self._paging = False
		self._ctrl_l = False
		self._ctrl_r = False
		self._stack = stack
		self._model = model
		self._view = view
		self._window = window
		self._plugin = plugin

		cur = window.get_active_tab()
		if cur:
			for tab in cur.parent.get_children():
				self.window_tab_added(window, tab, stack, model)
			self.window_active_tab_changed(window, cur, stack, model)

		self.connect_handlers(window, ('tab-added', 'tab-removed', 'active-tab-changed', 'key-press-event', 'key-release-event', 'focus-out-event'), 'window', stack, model)

	def deactivate(self):
		self.disconnect_handlers(self._window)

		self.end_switching()

		self._view.get_toplevel().destroy()

		self.disconnect_handlers(self._model)

		self._tabbing = None
		self._paging = None
		self._ctrl_l = None
		self._ctrl_r = None
		self._stack = None
		self._model = None
		self._view = None
		self._window = None
		self._plugin = None

	def update_ui(self):
		pass

	def model_row_changed(self, model, path, iter, view, sel):
		if model[path][self.SELECTED_TAB_COLUMN]:
			sel.select_path(path)
			view.scroll_to_cell(path, None, False, 0, 0)
		else:
			sel.unselect_path(path)

	def window_tab_added(self, window, tab, stack, model):
		if tab not in stack:
			stack.append(tab)
			model.append([self.tab_get_icon(tab), self.tab_get_name(tab), tab, False])

		self.connect_handlers(tab, ('notify::name', 'notify::state'), self.sync_icon_and_name, stack, model)

	def window_tab_removed(self, window, tab, stack, model):
		self.disconnect_handlers(tab)

		if tab in stack:
			model.remove(model.get_iter(stack.index(tab)))
			stack.remove(tab)

	def window_active_tab_changed(self, window, tab, stack, model):
		if not self._tabbing and not self._paging:
			if tab in stack:
				model.remove(model.get_iter(stack.index(tab)))
				stack.remove(tab)

			for row in model:
				row[self.SELECTED_TAB_COLUMN] = False

			stack.insert(0, tab)
			model.insert(0, [self.tab_get_icon(tab), self.tab_get_name(tab), tab, True])

	def sync_icon_and_name(self, tab, pspec, stack, model):
		if tab in stack:
			path = stack.index(tab)
			model[path][0] = self.tab_get_icon(tab)
			model[path][1] = self.tab_get_name(tab)

	def tab_get_name(self, tab):
		doc = tab.get_document()
		name = doc.get_short_name_for_display()
		docname = self.str_middle_truncate(name, self.MAX_DOC_NAME_LENGTH)

		if doc.get_modified():
			tab_name = '<i>%s</i>' % escape(docname)
		else:
			tab_name = docname

		if doc.get_readonly():
			tab_name += ' [<i>%s</i>]' % escape(_('Read Only'))

		return tab_name

	def tab_get_icon(self, tab):
		theme = gtk.icon_theme_get_for_screen(tab.get_screen())
		icon_size_width, icon_size_height = gtk.icon_size_lookup_for_settings(tab.get_settings(), gtk.ICON_SIZE_MENU)
		state = tab.get_state()

		if state in self.TAB_STATE_TO_ICON:
			try:
				pixbuf = self.get_stock_icon(theme, self.TAB_STATE_TO_ICON[state], icon_size_height)
			except glib.GError:
				pixbuf = None
		else:
			pixbuf = None

		if not pixbuf:
			uri = tab.get_document().get_uri()
			if uri:
				location = gio.File(uri)
			else:
				location = None
			pixbuf = self.get_icon(theme, location, icon_size_height)

		return pixbuf

	def window_key_press_event(self, window, event, stack, model):
		key = gtk.gdk.keyval_name(event.keyval)
		state = event.state & gtk.accelerator_get_default_mod_mask()

		if key == 'Control_L':
			self._ctrl_l = True

		if key == 'Control_R':
			self._ctrl_r = True

		if key in self.META_KEYS or not state & gtk.gdk.CONTROL_MASK:
			return False

		is_ctrl = state == gtk.gdk.CONTROL_MASK
		is_ctrl_shift = state == gtk.gdk.CONTROL_MASK | gtk.gdk.SHIFT_MASK
		is_tab_key = key in ('ISO_Left_Tab', 'Tab')
		is_page_key = key in ('Page_Up', 'Page_Down')
		is_up_dir = key in ('ISO_Left_Tab', 'Page_Up')

		if not (((is_ctrl or is_ctrl_shift) and is_tab_key) or (is_ctrl and is_page_key)):
			self.end_switching()
			return False

		cur = window.get_active_tab()
		if is_tab_key:
			tabs = stack
		else:
			tabs = cur.parent.get_children()
		tlen = len(tabs)

		if cur and tlen > 1 and cur in tabs:
			if is_up_dir:
				i = -1
			else:
				i = 1
			next = tabs[(tabs.index(cur) + i) % tlen]

			model[stack.index(cur)][self.SELECTED_TAB_COLUMN] = False
			model[stack.index(next)][self.SELECTED_TAB_COLUMN] = True

			if is_tab_key:
				view = self._view
				tabwin = view.get_toplevel()

				w, h = view.size_request()
				tabwin.set_size_request(-1, min(h, self.MAX_TAB_WINDOW_HEIGHT))
				tabwin.present()

				self._tabbing = True
			else:
				self._paging = True

			window.set_active_tab(next)

		return True

	def window_key_release_event(self, window, event, stack, model):
		key = gtk.gdk.keyval_name(event.keyval)

		if key == 'Control_L':
			self._ctrl_l = False

		if key == 'Control_R':
			self._ctrl_r = False

		if not self._ctrl_l and not self._ctrl_r:
			self.end_switching()

	def window_focus_out_event(self, window, event, stack, model):
		self.end_switching()

	def end_switching(self):
		if self._tabbing or self._paging:
			self._tabbing = False
			self._paging = False
			self._ctrl_l = False
			self._ctrl_r = False
			self._view.get_toplevel().hide()

			window = self._window
			tab = window.get_active_tab()
			if tab:
				self.window_active_tab_changed(window, tab, self._stack, self._model)

	def connect_handlers(self, obj, signals, m, *args):
		l_ids = obj.get_data(self.HANDLER_IDS)
		if not l_ids:
			l_ids = []

		for signal in signals:
			if type(m).__name__ == 'str':
				method = getattr(self, m + '_' + signal.replace('-', '_'))
			else:
				method = m
			l_ids.append(obj.connect(signal, method, *args))

		obj.set_data(self.HANDLER_IDS, l_ids)

	def disconnect_handlers(self, obj):
		l_ids = obj.get_data(self.HANDLER_IDS)
		if l_ids:
			for l_id in l_ids:
				obj.disconnect(l_id)

			obj.set_data(self.HANDLER_IDS, None)

	# following functions taken from gedit

	def str_middle_truncate(self, string, truncate_length):
		return self.str_truncate(string, truncate_length, True)

	def str_end_truncate(self, string, truncate_length):
		return self.str_truncate(string, truncate_length, False)

	def str_truncate(self, string, truncate_length, middle):
		delimiter = u'\u2026'

		# It doesnt make sense to truncate strings to less than
		# the size of the delimiter plus 2 characters (one on each
		# side)
		delimiter_length = len(delimiter)
		if truncate_length < (delimiter_length + 2):
			return string

		n_chars = len(string)

		# Make sure the string is not already small enough.
		if n_chars <= truncate_length:
			return string

		# Find the 'middle' where the truncation will occur.
		if middle:
			num_left_chars = (truncate_length - delimiter_length) / 2
			right_offset = n_chars - truncate_length + num_left_chars + delimiter_length

			truncated = string[:num_left_chars] + delimiter + string[right_offset:]
		else:
			num_left_chars = truncate_length - delimiter_length
			truncated = string[:num_left_chars] + delimiter

		return truncated

	def get_stock_icon(self, theme, stock, size):
		pixbuf = theme.load_icon(stock, size, 0)
		return self.resize_icon(pixbuf, size)

	def get_icon(self, theme, location, size):
		if not location:
			return self.get_stock_icon(theme, gtk.STOCK_FILE, size)

		# FIXME: Doing a sync stat is bad, this should be fixed
		try:
			info = location.query_info(gio.FILE_ATTRIBUTE_STANDARD_ICON, gio.FILE_QUERY_INFO_NONE, None)
		except gio.Error:
			info = None

		if not info:
			return self.get_stock_icon(theme, gtk.STOCK_FILE, size)

		icon = info.get_icon()

		if not icon:
			return self.get_stock_icon(theme, gtk.STOCK_FILE, size)

		icon_info = theme.lookup_by_gicon(icon, size, 0);

		if not icon_info:
			return self.get_stock_icon(theme, gtk.STOCK_FILE, size)

		pixbuf = icon_info.load_icon()

		if not pixbuf:
			return self.get_stock_icon(theme, gtk.STOCK_FILE, size)

		return self.resize_icon(pixbuf, size)

	def resize_icon(self, pixbuf, size):
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

			pixbuf = pixbuf.scale_simple(width, height, gtk.gdk.INTERP_BILINEAR)

		return pixbuf

class ControlYourTabsPlugin(gedit.Plugin):
	def __init__(self):
		gedit.Plugin.__init__(self)
		self._instances = {}

	def activate(self, window):
		self._instances[window] = ControlYourTabsWindowHelper(self, window)

	def deactivate(self, window):
		self._instances[window].deactivate()
		del self._instances[window]

	def update_ui(self, window):
		self._instances[window].update_ui()

