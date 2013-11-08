# -*- coding: utf-8 -*-
#
# controlyourtabs.py
# This file is part of Control Your Tabs, a plugin for gedit
#
# Copyright (C) 2010-2013 Jeffery To <jeffery.to@gmail.com>
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

	# based on MAX_DOC_NAME_LENGTH in gedit-documents-panel.c
	MAX_DOC_NAME_LENGTH = 60

	MAX_TAB_WINDOW_HEIGHT = 250

	# based on switch statement in _gedit_tab_get_icon() in gedit-tab.c
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

		col = Gtk.TreeViewColumn(_("Documents"))
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

		tab = window.get_active_tab()
		if tab:
			self._setup(tab)
			if self._multi:
				self.on_window_active_tab_changed(window, tab, notebooks)

		if not self._multi:
			self._connect_handlers(window, ('tab-added',), 'window')

	def do_deactivate(self):
		self._disconnect_handlers(self.window)

		self._end_switching()

		notebooks = self._notebooks
		for notebook in notebooks:
			self._disconnect_handlers(notebooks[notebook][1])

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

	def on_window_tab_added(self, window, tab):
		self._disconnect_handlers(window)
		self._setup(tab)

	def _setup(self, tab):
		notebooks = self._notebooks
		multi = self._get_multi_notebook(tab)

		if multi:
			self._connect_handlers(multi, ('notebook-added', 'notebook-removed', 'tab-added', 'tab-removed'), 'multi_notebook', notebooks)
			self._multi = multi

			for doc in self.window.get_documents():
				self.on_multi_notebook_notebook_added(multi, Gedit.Tab.get_from_document(doc).get_parent(), notebooks)

			self._connect_handlers(self.window, ('tabs-reordered', 'active-tab-changed', 'key-press-event', 'key-release-event', 'focus-out-event'), 'window', notebooks)

		elif hasattr(Gedit, 'debug_plugin_message'):
			Gedit.debug_plugin_message("cannot find multi notebook from %s", tab)

	def on_multi_notebook_notebook_added(self, multi, notebook, notebooks):
		if notebook not in notebooks:
			model = Gtk.ListStore(GdkPixbuf.Pixbuf, str, Gedit.Tab, 'gboolean')
			view = self._view
			self._connect_handlers(model, ('row-changed',), 'model', view, view.get_selection())
			notebooks[notebook] = [[], model]

			for tab in notebook.get_children():
				self.on_multi_notebook_tab_added(multi, notebook, tab, notebooks)

	def on_multi_notebook_notebook_removed(self, multi, notebook, notebooks):
		if notebook in notebooks:
			for tab in notebook.get_children():
				self.on_multi_notebook_tab_removed(multi, notebook, tab, notebooks)

			stack, model = notebooks[notebook]
			view = self._view
			if view.get_model() == model:
				view.set_model(None)
			self._disconnect_handlers(model)
			del notebooks[notebook]

	def on_multi_notebook_tab_added(self, multi, notebook, tab, notebooks):
		stack, model = notebooks[notebook]
		if tab not in stack:
			stack.append(tab)
			model.append([self._get_tab_icon(tab), self._get_tab_name(tab), tab, False])
			self._connect_handlers(tab, ('notify::name', 'notify::state'), self.on_sync_icon_and_name, notebooks)

	def on_multi_notebook_tab_removed(self, multi, notebook, tab, notebooks):
		stack, model = notebooks[notebook]
		if tab in stack:
			self._disconnect_handlers(tab)
			model.remove(model.get_iter(stack.index(tab)))
			stack.remove(tab)

	def on_model_row_changed(self, model, path, iter, view, sel):
		if view.get_model() == model:
			if model[path][self.SELECTED_TAB_COLUMN]:
				sel.select_path(path)
				view.scroll_to_cell(path, None, False, 0, 0)
			else:
				sel.unselect_path(path)

	def on_window_tabs_reordered(self, window, notebooks):
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
				self.on_multi_notebook_tab_removed(multi, old_notebook, tab, notebooks)
			self.on_multi_notebook_tab_added(multi, new_notebook, tab, notebooks)

	def on_window_active_tab_changed(self, window, tab, notebooks):
		if not self._tabbing and not self._paging:
			stack, model = notebooks[tab.get_parent()]
			if tab in stack:
				model.remove(model.get_iter(stack.index(tab)))
				stack.remove(tab)

			self._view.set_model(model)

			for row in model:
				row[self.SELECTED_TAB_COLUMN] = False

			stack.insert(0, tab)
			model.insert(0, [self._get_tab_icon(tab), self._get_tab_name(tab), tab, True])

	def on_sync_icon_and_name(self, tab, pspec, notebooks):
		stack, model = notebooks[tab.get_parent()]
		if tab in stack:
			path = stack.index(tab)
			model[path][0] = self._get_tab_icon(tab)
			model[path][1] = self._get_tab_name(tab)

	def on_window_key_press_event(self, window, event, notebooks):
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

	def on_window_key_release_event(self, window, event, notebooks):
		key = Gdk.keyval_name(event.keyval)

		if key == 'Control_L':
			self._ctrl_l = False

		if key == 'Control_R':
			self._ctrl_r = False

		if not self._ctrl_l and not self._ctrl_r:
			self._end_switching()

	def on_window_focus_out_event(self, window, event, notebooks):
		self._end_switching()

	def _end_switching(self):
		if self._tabbing or self._paging:
			self._tabbing = False
			self._paging = False
			self._ctrl_l = False
			self._ctrl_r = False
			self._view.get_toplevel().hide()

			window = self.window
			tab = window.get_active_tab()
			if tab:
				self.on_window_active_tab_changed(window, tab, self._notebooks)

	# based on tab_get_name() in gedit-documents-panel.c
	def _get_tab_name(self, tab):
		doc = tab.get_document()
		name = doc.get_short_name_for_display()
		docname = Gedit.utils_str_middle_truncate(name, self.MAX_DOC_NAME_LENGTH)

		if doc.get_modified():
			tab_name = "<i>%s</i>" % escape(docname)
		else:
			tab_name = escape(docname)

		if doc.get_readonly():
			tab_name += " [<i>%s</i>]" % escape(_("Read Only"))

		return tab_name

	# based on _gedit_tab_get_icon() in gedit-tab.c
	def _get_tab_icon(self, tab):
		theme = Gtk.IconTheme.get_for_screen(tab.get_screen())
		is_valid_size, icon_size_width, icon_size_height = Gtk.icon_size_lookup_for_settings(tab.get_settings(), Gtk.IconSize.MENU)
		state = tab.get_state()

		if state in self.TAB_STATE_TO_ICON:
			try:
				pixbuf = self._get_stock_icon(theme, self.TAB_STATE_TO_ICON[state], icon_size_height)
			except GObject.GError:
				pixbuf = None
		else:
			pixbuf = None

		if not pixbuf:
			pixbuf = self._get_icon(theme, tab.get_document().get_location(), icon_size_height)

		return pixbuf

	# based on get_stock_icon() in gedit-tab.c
	def _get_stock_icon(self, theme, stock, size):
		pixbuf = theme.load_icon(stock, size, 0)
		return self._resize_icon(pixbuf, size)

	# based on get_icon() in gedit-tab.c
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

	# based on resize_icon() in gedit-tab.c
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

			pixbuf = pixbuf.scale_simple(width, height, Gdk.INTERP_BILINEAR)

		return pixbuf

	def _connect_handlers(self, obj, signals, m, *args):
		HANDLER_IDS = self.HANDLER_IDS
		l_ids = getattr(obj, HANDLER_IDS) if hasattr(obj, HANDLER_IDS) else []

		for signal in signals:
			if type(m).__name__ == 'str':
				method = getattr(self, 'on_' + m + '_' + signal.replace('-', '_').replace('::', '_'))
			else:
				method = m
			l_ids.append(obj.connect(signal, method, *args))

		setattr(obj, HANDLER_IDS, l_ids)

	def _disconnect_handlers(self, obj):
		HANDLER_IDS = self.HANDLER_IDS
		if hasattr(obj, HANDLER_IDS):
			for l_id in getattr(obj, HANDLER_IDS):
				obj.disconnect(l_id)

			delattr(obj, HANDLER_IDS)

	# this is a /hack/
	def _get_multi_notebook(self, tab):
		multi = tab.get_parent()
		while multi:
			if multi.__gtype__.name == 'GeditMultiNotebook':
				break
			multi = multi.get_parent()
		return multi
