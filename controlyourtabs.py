# -*- coding: utf-8 -*-
#
# Control Your Tabs, a plugin for gedit
# Switch between tabs using Ctrl+Tab / Ctrl+Shift+Tab and
# Ctrl+PageUp / Ctrl+PageDown
# v0.2.0
#
# Copyright (C) 2010-2011 Jeffery To <jeffery.to@gmail.com>
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

from gi.repository import GObject, Gtk, Gdk, GdkPixbuf, Gio, Gedit
from gettext import gettext as _
from xml.sax.saxutils import escape

class ControlYourTabsPlugin(GObject.Object, Gedit.WindowActivatable):
	__gtype_name__ = 'ControlYourTabsPlugin'

	window = GObject.property(type=Gedit.Window)

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

		col = Gtk.TreeViewColumn(_('Documents'))
		col.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
		cell = Gtk.CellRendererPixbuf()
		col.pack_start(cell, False)
		col.add_attribute(cell, 'pixbuf', 0)
		cell = Gtk.CellRendererText()
		col.pack_start(cell, True)
		col.add_attribute(cell, 'markup', 1)

		view.append_column(col)

		sel = view.get_selection()
		sel.set_mode(Gtk.SelectionMode.SINGLE)

		self._tabbing = False
		self._paging = False
		self._ctrl_l = False
		self._ctrl_r = False
		self._multi = None
		self._notebooks = notebooks
		self._view = view

		cur = window.get_active_tab()
		if cur:
			self.setup(cur)
			if self._multi:
				self.window_active_tab_changed(window, cur, notebooks)

		if not self._multi:
			self.connect_handlers(window, ('tab-added',), 'window')

	def do_deactivate(self):
		self.disconnect_handlers(self.window)

		self.end_switching()

		notebooks = self._notebooks
		for notebook in notebooks:
			self.disconnect_handlers(notebooks[notebook][1])

		self._view.get_toplevel().destroy()

		self._tabbing = None
		self._paging = None
		self._ctrl_l = None
		self._ctrl_r = None
		self._multi = None
		self._notebooks = None
		self._view = None

	def do_update_state(self):
		pass

	def setup(self, cur):
		notebooks = self._notebooks
		multi = self.get_multi_notebook(cur)

		if multi:
			self.connect_handlers(multi, ('notebook-added', 'notebook-removed', 'tab-added', 'tab-removed'), 'multi_notebook', notebooks)
			self._multi = multi

			for doc in self.window.get_documents():
				self.multi_notebook_notebook_added(multi, Gedit.Tab.get_from_document(doc).get_parent(), notebooks)

			self.connect_handlers(self.window, ('tabs-reordered', 'active-tab-changed', 'key-press-event', 'key-release-event', 'focus-out-event'), 'window', notebooks)

		else:
			print 'ControlYourTabsPlugin: cannot find multi notebook from', cur

	def multi_notebook_notebook_added(self, multi, notebook, notebooks):
		if notebook not in notebooks:
			model = Gtk.ListStore(GdkPixbuf.Pixbuf, str, Gedit.Tab, 'gboolean')
			view = self._view
			self.connect_handlers(model, ('row-changed',), 'model', view, view.get_selection())
			notebooks[notebook] = [[], model]

			for tab in notebook.get_children():
				self.multi_notebook_tab_added(multi, notebook, tab, notebooks)

	def multi_notebook_notebook_removed(self, multi, notebook, notebooks):
		if notebook in notebooks:
			for tab in notebook.get_children():
				self.multi_notebook_tab_removed(multi, notebook, tab, notebooks)

			stack, model = notebooks[notebook]
			view = self._view
			if view.get_model() == model:
				view.set_model(None)
			self.disconnect_handlers(model)
			del notebooks[notebook]

	def multi_notebook_tab_added(self, multi, notebook, tab, notebooks):
		stack, model = notebooks[notebook]
		if tab not in stack:
			stack.append(tab)
			model.append([self.tab_get_icon(tab), self.tab_get_name(tab), tab, False])
			self.connect_handlers(tab, ('notify::name', 'notify::state'), self.sync_icon_and_name, notebooks)

	def multi_notebook_tab_removed(self, multi, notebook, tab, notebooks):
		stack, model = notebooks[notebook]
		if tab in stack:
			self.disconnect_handlers(tab)
			model.remove(model.get_iter(stack.index(tab)))
			stack.remove(tab)

	def model_row_changed(self, model, path, iter, view, sel):
		if view.get_model() == model:
			if model[path][self.SELECTED_TAB_COLUMN]:
				sel.select_path(path)
				view.scroll_to_cell(path, None, False, 0, 0)
			else:
				sel.unselect_path(path)

	def window_tab_added(self, window, tab):
		if not self._multi:
			self.setup(tab)

	def window_tabs_reordered(self, window, notebooks):
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
				self.multi_notebook_tab_removed(multi, old_notebook, tab, notebooks)
			self.multi_notebook_tab_added(multi, new_notebook, tab, notebooks)

	def window_active_tab_changed(self, window, tab, notebooks):
		if not self._tabbing and not self._paging:
			stack, model = notebooks[tab.get_parent()]
			if tab in stack:
				model.remove(model.get_iter(stack.index(tab)))
				stack.remove(tab)

			self._view.set_model(model)

			for row in model:
				row[self.SELECTED_TAB_COLUMN] = False

			stack.insert(0, tab)
			model.insert(0, [self.tab_get_icon(tab), self.tab_get_name(tab), tab, True])

	def sync_icon_and_name(self, tab, pspec, notebooks):
		stack, model = notebooks[tab.get_parent()]
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
		theme = Gtk.IconTheme.get_for_screen(tab.get_screen())
		is_valid_size, icon_size_width, icon_size_height = Gtk.icon_size_lookup_for_settings(tab.get_settings(), Gtk.IconSize.MENU)
		state = tab.get_state()

		if state in self.TAB_STATE_TO_ICON:
			try:
				pixbuf = self.get_stock_icon(theme, self.TAB_STATE_TO_ICON[state], icon_size_height)
			except GObject.GError:
				pixbuf = None
		else:
			pixbuf = None

		if not pixbuf:
			pixbuf = self.get_icon(theme, tab.get_document().get_location(), icon_size_height)

		return pixbuf

	def window_key_press_event(self, window, event, notebooks):
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
			self.end_switching()
			return False

		cur = window.get_active_tab()
		if cur:
			notebook = cur.get_parent()
			stack, model = notebooks[notebook]
			if is_tab_key:
				tabs = stack
			else:
				tabs = notebook.get_children()
			tlen = len(tabs)

			if tlen > 1 and cur in tabs:
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

					min_size, nat_size = view.get_preferred_size()
					tabwin.set_size_request(-1, min(nat_size.height, self.MAX_TAB_WINDOW_HEIGHT))
					tabwin.present()

					self._tabbing = True
				else:
					self._paging = True

				window.set_active_tab(next)

		return True

	def window_key_release_event(self, window, event, notebooks):
		key = Gdk.keyval_name(event.keyval)

		if key == 'Control_L':
			self._ctrl_l = False

		if key == 'Control_R':
			self._ctrl_r = False

		if not self._ctrl_l and not self._ctrl_r:
			self.end_switching()

	def window_focus_out_event(self, window, event, notebooks):
		self.end_switching()

	def end_switching(self):
		if self._tabbing or self._paging:
			self._tabbing = False
			self._paging = False
			self._ctrl_l = False
			self._ctrl_r = False
			self._view.get_toplevel().hide()

			window = self.window
			tab = window.get_active_tab()
			if tab:
				self.window_active_tab_changed(window, tab, self._notebooks)

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

	# this is a /hack/

	def get_multi_notebook(self, tab):
		multi = tab.get_parent()
		while multi:
			if multi.__gtype__.name == 'GeditMultiNotebook':
				break
			multi = multi.get_parent()
		return multi

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
			return self.get_stock_icon(theme, Gtk.STOCK_FILE, size)

		# FIXME: Doing a sync stat is bad, this should be fixed
		try:
			info = location.query_info(Gio.FILE_ATTRIBUTE_STANDARD_ICON, Gio.FileQueryInfoFlags.NONE, None)
		except GObject.GError:
			info = None

		if not info:
			return self.get_stock_icon(theme, Gtk.STOCK_FILE, size)

		icon = info.get_icon()

		if not icon:
			return self.get_stock_icon(theme, Gtk.STOCK_FILE, size)

		icon_info = theme.lookup_by_gicon(icon, size, 0);

		if not icon_info:
			return self.get_stock_icon(theme, Gtk.STOCK_FILE, size)

		pixbuf = icon_info.load_icon()

		if not pixbuf:
			return self.get_stock_icon(theme, Gtk.STOCK_FILE, size)

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

			pixbuf = pixbuf.scale_simple(width, height, Gdk.INTERP_BILINEAR)

		return pixbuf
