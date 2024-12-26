# -*- coding: utf-8 -*-
#
# windowactivatable.py
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
gi.require_version('GLib', '2.0')
gi.require_version('GObject', '2.0')
gi.require_version('Gdk', '3.0')
gi.require_version('Gtk', '3.0')

import math
from gi.repository import GLib, GObject, Gdk, Gtk
from .plugin import _
from .settings import get_settings
from .tabmodel import ControlYourTabsTabModel
from .utils import connect_handlers, disconnect_handlers
from . import editor, keyinfo, log, tabinfo


class ControlYourTabsWindowActivatable(GObject.Object, editor.Editor.WindowActivatable):

	__gtype_name__ = 'ControlYourTabsWindowActivatable'

	window = GObject.property(type=editor.Editor.Window) # before pygobject 3.2, lowercase 'p'

	MAX_TAB_WINDOW_ROWS = 9

	MAX_TAB_WINDOW_HEIGHT_PERCENTAGE = 0.5


	def __init__(self):
		GObject.Object.__init__(self)

	def do_activate(self):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s", self.window))

		window = self.window
		tab_models = {}

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

		self._is_switching = False
		self._is_tabwin_visible = False
		self._is_control_held = keyinfo.default_control_held()
		self._pre_key_press_control_keys = None
		self._initial_tab = None
		self._multi = None
		self._tab_models = tab_models
		self._tabwin = tabwin
		self._view = view
		self._sw = sw
		self._icon_cell = icon_cell
		self._space_cell = space_cell
		self._tabwin_resize_id = None
		self._settings = get_settings()

		tab = window.get_active_tab()

		if tab:
			if log.query(log.INFO):
				editor.debug_plugin_message(log.format("Found active tab %s, setting up now", tab))

			self.setup(window, tab, tab_models)

		else:
			if log.query(log.INFO):
				editor.debug_plugin_message(log.format("Waiting for new tab"))

			connect_handlers(
				self, window,
				['tab-added'],
				'setup',
				tab_models
			)

	def do_deactivate(self):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s", self.window))

		multi = self._multi
		tab_models = self._tab_models

		for notebook in list(tab_models.keys()):
			self.untrack_notebook(notebook, tab_models)

		if multi:
			disconnect_handlers(self, multi)

		disconnect_handlers(self, self.window)

		self.cancel_tabwin_resize()
		self.end_switching()

		self._tabwin.destroy()

		self._is_switching = None
		self._is_tabwin_visible = None
		self._is_control_held = None
		self._pre_key_press_control_keys = None
		self._initial_tab = None
		self._multi = None
		self._tab_models = None
		self._tabwin = None
		self._view = None
		self._sw = None
		self._icon_cell = None
		self._space_cell = None
		self._tabwin_resize_id = None
		self._settings = None

	def do_update_state(self):
		pass


	# plugin setup

	def on_setup_tab_added(self, window, tab, tab_models):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s, %s", window, tab))

		disconnect_handlers(self, window)

		self.setup(window, tab, tab_models)

	def setup(self, window, tab, tab_models):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s, %s", window, tab))

		icon_size = tabinfo.get_tab_icon_size()

		self._icon_cell.set_fixed_size(icon_size, icon_size)
		self._space_cell.set_fixed_size(icon_size, icon_size)

		multi = window.get_template_child(editor.Editor.Window, 'multi_notebook')

		if multi:
			connect_handlers(
				self, multi,
				[
					'notebook-added',
					'notebook-removed',
					'tab-added',
					'tab-removed'
				],
				'multi_notebook',
				tab_models
			)
		else:
			connect_handlers(
				self, window,
				[
					'tab-added',
					'tab-removed'
				],
				'window',
				tab.get_parent(), tab_models
			)

		connect_handlers(
			self, window,
			[
				'active-tab-changed',
				'key-press-event',
				'key-release-event',
				'focus-out-event',
				'configure-event'
			],
			'window',
			tab_models
		)

		if editor.use_editor_workaround:
			connect_handlers(
				self, window,
				[
					'event',
					'event-after'
				],
				'window'
			)

		self._multi = multi

		for document in window.get_documents():
			notebook = editor.Editor.Tab.get_from_document(document).get_parent()
			self.track_notebook(notebook, tab_models, is_setup=True)

		self.active_tab_changed(tab, tab_models[tab.get_parent()])


	# tracking notebooks / tabs

	def track_notebook(self, notebook, tab_models, is_setup=False):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s, %s", self.window, notebook))

		if notebook in tab_models:
			if log.query(log.DEBUG if is_setup else log.WARNING):
				editor.debug_plugin_message(log.format("Already tracking %s", notebook))

			return

		tab_model = ControlYourTabsTabModel()

		connect_handlers(
			self, tab_model,
			[
				'row-inserted',
				'row-deleted',
				'row-changed'
			],
			self.on_tab_model_row_changed
		)
		connect_handlers(
			self, tab_model,
			['selected-path-changed'],
			'tab_model'
		)

		tab_models[notebook] = tab_model

		for tab in notebook.get_children():
			self.track_tab(tab, tab_model)

	def untrack_notebook(self, notebook, tab_models):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s, %s", self.window, notebook))

		if notebook not in tab_models:
			if log.query(log.WARNING):
				editor.debug_plugin_message(log.format("Not tracking %s", notebook))

			return

		tab_model = tab_models[notebook]

		for tab in notebook.get_children():
			self.untrack_tab(tab, tab_model)

		if self.is_active_view_model(tab_model):
			self.set_active_view_model(None)

		disconnect_handlers(self, tab_model)

		del tab_models[notebook]

	def track_tab(self, tab, tab_model):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s, %s", self.window, tab))

		if tab in tab_model:
			if log.query(log.WARNING):
				editor.debug_plugin_message(log.format("Already tracking %s", tab))

			return

		tab_model.append(tab)

		connect_handlers(
			self, tab,
			[
				'notify::name',
				'notify::state'
			],
			self.on_tab_notify_name_state,
			tab_model
		)

	def untrack_tab(self, tab, tab_model):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s, %s", self.window, tab))

		if tab is self._initial_tab:
			if log.query(log.DEBUG):
				editor.debug_plugin_message(log.format("Tab is initial tab, clearing"))

			self._initial_tab = None

		if tab not in tab_model:
			if log.query(log.WARNING):
				editor.debug_plugin_message(log.format("Not tracking %s", tab))

			return

		disconnect_handlers(self, tab)

		tab_model.remove(tab)

	def active_tab_changed(self, tab, tab_model):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s, %s", self.window, tab))

		if not self._is_switching:
			tab_model.move_after(tab)

		tab_model.select(tab)

		if not self.is_active_view_model(tab_model):
			self.set_active_view_model(tab_model)
			self.schedule_tabwin_resize()


	# signal handlers

	def on_multi_notebook_notebook_added(self, multi, notebook, tab_models):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s, %s", self.window, notebook))

		self.track_notebook(notebook, tab_models)

	def on_multi_notebook_notebook_removed(self, multi, notebook, tab_models):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s, %s", self.window, notebook))

		self.untrack_notebook(notebook, tab_models)

	def on_multi_notebook_tab_added(self, multi, notebook, tab, tab_models):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s, %s, %s", self.window, notebook, tab))

		self.track_tab(tab, tab_models[notebook])

	def on_multi_notebook_tab_removed(self, multi, notebook, tab, tab_models):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s, %s, %s", self.window, notebook, tab))

		self.untrack_tab(tab, tab_models[notebook])

	def on_window_tab_added(self, window, tab, notebook, tab_models):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s, %s, %s", window, notebook, tab))

		self.track_tab(tab, tab_models[notebook])

	def on_window_tab_removed(self, window, tab, notebook, tab_models):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s, %s, %s", window, notebook, tab))

		self.untrack_tab(tab, tab_models[notebook])

	def on_window_active_tab_changed(self, window, tab, tab_models=None):
		# tab parameter removed in gedit 47
		if not tab_models:
			tab_models = tab
			tab = window.get_active_tab()

		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s, %s", window, tab))

		if tab:
			tab_model = tab_models[tab.get_parent()]

			# in pluma/xed, when a tab is added to an empty notebook,
			# active-tab-changed is emitted before tab-added
			if tab not in tab_model:
				self.track_tab(tab, tab_model)

			self.active_tab_changed(tab, tab_model)

	def on_window_key_press_event(self, window, event, tab_models):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s, key=%s", window, Gdk.keyval_name(event.keyval)))

		self._is_control_held = keyinfo.update_control_held(event, self._is_control_held, True)

		return self.key_press_event(event)

	def on_window_key_release_event(self, window, event, tab_models):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s, key=%s", self.window, Gdk.keyval_name(event.keyval)))

		self._is_control_held = keyinfo.update_control_held(event, self._is_control_held, False)

		if not any(self._is_control_held):
			if log.query(log.DEBUG):
				editor.debug_plugin_message(log.format("No control keys held down"))

			self.end_switching()

		else:
			if log.query(log.DEBUG):
				editor.debug_plugin_message(log.format("One or more control keys held down"))

	def on_window_focus_out_event(self, window, event, tab_models):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s", window))

		self.end_switching()

	def on_window_configure_event(self, window, event, tab_models):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s", window))

		self.schedule_tabwin_resize()

	def on_window_event(self, window, event):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s", window))

		if event.type is Gdk.EventType.KEY_PRESS:
			self.pre_key_press_event(event)

	def on_window_event_after(self, window, event):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s", window))

		if event.type is Gdk.EventType.KEY_PRESS:
			self._pre_key_press_control_keys = None

	def on_tab_notify_name_state(self, tab, pspec, tab_model):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s, %s", self.window, tab))

		tab_model.update(tab)

	def on_tab_model_row_changed(self, tab_model, path):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s, path=%s", self.window, path))

		if not self.is_active_view_model(tab_model):
			if log.query(log.DEBUG):
				editor.debug_plugin_message(log.format("Tab model not active"))

			return

		self.schedule_tabwin_resize()

	def on_tab_model_selected_path_changed(self, tab_model, path):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s, path=%s", self.window, path))

		if not self.is_active_view_model(tab_model):
			if log.query(log.DEBUG):
				editor.debug_plugin_message(log.format("Tab model not active"))

			return

		self.set_view_selection(path)


	# tree view

	def is_active_view_model(self, tab_model):
		model = tab_model.model if tab_model else None
		return self._view.get_model() is model

	def set_active_view_model(self, tab_model):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s, %s", self.window, tab_model))

		model = None
		selected_path = None

		if tab_model:
			model = tab_model.model
			selected_path = tab_model.get_selected_path()

		self._view.set_model(model)
		self.set_view_selection(selected_path)

	def set_view_selection(self, path):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s, path=%s", self.window, path))

		view = self._view
		selection = view.get_selection()

		if path:
			selection.select_path(path)
			view.scroll_to_cell(path, None, True, 0.5, 0)

		else:
			selection.unselect_all()


	# tab switching/moving

	def pre_key_press_event(self, event):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s, key=%s", self.window, Gdk.keyval_name(event.keyval)))

		is_control = keyinfo.is_control_keys(event)

		if is_control.tab_key:
			if log.query(log.DEBUG):
				editor.debug_plugin_message(log.format("Applying editor workaround for Ctrl-Tab"))

			event.state &= ~keyinfo.CONTROL_MASK
			self._pre_key_press_control_keys = is_control

		elif self._is_switching and is_control.escape_key:
			if log.query(log.DEBUG):
				editor.debug_plugin_message(log.format("Applying editor workaround for Ctrl-Esc"))

			event.keyval = Gdk.KEY_VoidSymbol
			self._pre_key_press_control_keys = is_control

	def key_press_event(self, event):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s, key=%s", self.window, Gdk.keyval_name(event.keyval)))

		settings = self._settings
		block_event = False

		if self._pre_key_press_control_keys:
			if log.query(log.DEBUG):
				editor.debug_plugin_message(log.format("Completing editor workaround"))

			is_control = self._pre_key_press_control_keys

			if is_control.tab_key:
				event.state |= keyinfo.CONTROL_MASK

			elif self._is_switching and is_control.escape_key:
				event.keyval = Gdk.KEY_Escape

			self._pre_key_press_control_keys = None

		else:
			is_control = keyinfo.is_control_keys(event)

		if is_control.tab_key and settings and settings['use-tabbar-order']:
			if log.query(log.INFO):
				editor.debug_plugin_message(log.format("Coercing Ctrl-Tab into Ctrl-PgUp/PgDn because of settings"))

			is_control = is_control._replace(
				tab=False, shift_tab=False, tab_key=False,
				page_up=is_control.shift_tab,
				page_up_key=is_control.shift_tab,
				page_down=is_control.tab,
				page_down_key=is_control.tab
			)

		if is_control.tab_key or is_control.page_up or is_control.page_down:
			if log.query(log.INFO):
				editor.debug_plugin_message(log.format("Ctrl-Tab or Ctrl-PgUp/PgDn, switch tab"))

			self.switch_tab(
				use_mru_order=is_control.tab_key,
				to_next_tab=is_control.tab or is_control.page_down,
				time=event.time
			)
			block_event = True

		elif is_control.shift_page_up or is_control.shift_page_down:
			if log.query(log.INFO):
				editor.debug_plugin_message(log.format("Ctrl-Shift-PgUp/PgDn, move tab"))

			self.end_switching()
			self.move_tab(to_right=is_control.shift_page_down)
			block_event = True

		elif self._is_switching:
			if is_control.escape_key:
				if log.query(log.INFO):
					editor.debug_plugin_message(log.format("Ctrl-Esc while switching, cancel tab switching"))

				self.end_switching(do_revert=True)
				block_event = True

			elif keyinfo.is_modifier_key(event):
				if log.query(log.INFO):
					editor.debug_plugin_message(log.format("Modifier key while switching, no action"))

			elif not self._is_tabwin_visible:
				if log.query(log.INFO):
					editor.debug_plugin_message(log.format("Normal key while switching and tabwin not visible, end tab switching"))

				self.end_switching()

			else:
				if log.query(log.INFO):
					editor.debug_plugin_message(log.format("Normal key while switching, block key press"))

				block_event = True

		else:
			if log.query(log.DEBUG):
				editor.debug_plugin_message(log.format("Normal key, no action"))

		return block_event

	def switch_tab(self, use_mru_order, to_next_tab, time):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s, use_mru_order=%s, to_next_tab=%s, time=%s", self.window, use_mru_order, to_next_tab, time))

		window = self.window
		current_tab = window.get_active_tab()

		if not current_tab:
			if log.query(log.INFO):
				editor.debug_plugin_message(log.format("No tabs"))

			return

		notebook = current_tab.get_parent()

		tabs = self._tab_models[notebook] if use_mru_order else notebook.get_children()
		num_tabs = len(tabs)

		if num_tabs < 2:
			if log.query(log.INFO):
				editor.debug_plugin_message(log.format("Only 1 tab"))

			return

		current_index = tabs.index(current_tab)
		step = 1 if to_next_tab else -1
		next_index = (current_index + step) % num_tabs

		next_tab = tabs[next_index]

		if log.query(log.INFO):
			editor.debug_plugin_message(log.format("Switching from %s to %s", current_tab, next_tab))

		if not self._is_switching:
			if log.query(log.INFO):
				editor.debug_plugin_message(log.format("Saving %s as initial tab", current_tab))

			self._initial_tab = current_tab

		self._is_switching = True

		window.set_active_tab(next_tab)

		if use_mru_order:
			tabwin = self._tabwin

			if not self._is_tabwin_visible:
				if log.query(log.INFO):
					editor.debug_plugin_message(log.format("Showing tabwin"))

				tabwin.show_all()

			else:
				if log.query(log.INFO):
					editor.debug_plugin_message(log.format("Presenting tabwin"))

				tabwin.present_with_time(time)

			self._is_tabwin_visible = True

	def end_switching(self, do_revert=False):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s, do_revert=%s", self.window, do_revert))

		if not self._is_switching:
			if log.query(log.DEBUG):
				editor.debug_plugin_message(log.format("Not switching"))

			return

		window = self.window
		initial_tab = self._initial_tab

		self._tabwin.hide()

		self._is_switching = False
		self._is_tabwin_visible = False
		self._initial_tab = None

		if do_revert and initial_tab:
			if log.query(log.INFO):
				editor.debug_plugin_message(log.format("Switching to initial tab %s", initial_tab))

			window.set_active_tab(initial_tab)

		else:
			tab = window.get_active_tab()

			if tab:
				self.active_tab_changed(tab, self._tab_models[tab.get_parent()])

	def move_tab(self, to_right):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s, to_right=%s", self.window, to_right))

		window = self.window
		current_tab = window.get_active_tab()

		if not current_tab:
			if log.query(log.INFO):
				editor.debug_plugin_message(log.format("No tabs"))

			return

		notebook = current_tab.get_parent()
		tabs = notebook.get_children()
		num_tabs = len(tabs)

		if num_tabs < 2:
			if log.query(log.INFO):
				editor.debug_plugin_message(log.format("Only 1 tab"))

			return

		current_index = tabs.index(current_tab)
		step = 1 if to_right else -1
		next_index = (current_index + step) % num_tabs

		try:
			notebook.reorder_tab(current_tab, next_index)
		except AttributeError:
			notebook.reorder_child(current_tab, next_index)


	# tab window resizing

	def schedule_tabwin_resize(self):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s", self.window))

		if self._tabwin_resize_id:
			if log.query(log.DEBUG):
				editor.debug_plugin_message(log.format("Already scheduled"))

			return

		# need to wait a little before asking the treeview for its preferred size
		# maybe because treeview rendering is async?
		# this feels like a giant hack
		try:
			resize_id = GLib.idle_add(self.do_tabwin_resize)
		except TypeError: # before pygobject 3.0
			resize_id = GObject.idle_add(self.do_tabwin_resize)

		self._tabwin_resize_id = resize_id

	def cancel_tabwin_resize(self):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s", self.window))

		if not self._tabwin_resize_id:
			if log.query(log.DEBUG):
				editor.debug_plugin_message(log.format("Not scheduled"))

			return

		GLib.source_remove(self._tabwin_resize_id)

		self._tabwin_resize_id = None

	def do_tabwin_resize(self):
		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("%s", self.window))

		view = self._view
		sw = self._sw

		view_min_size, view_nat_size = view.get_preferred_size()
		view_height = max(view_min_size.height, view_nat_size.height)

		num_rows = len(view.get_model())
		if num_rows:
			row_height = math.ceil(view_height / num_rows)
			max_rows_height = self.MAX_TAB_WINDOW_ROWS * row_height
		else:
			max_rows_height = float('inf')

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

		if log.query(log.DEBUG):
			editor.debug_plugin_message(log.format("view height     = %s", view_height))
			editor.debug_plugin_message(log.format("max rows height = %s", max_rows_height))
			editor.debug_plugin_message(log.format("max win height  = %s", max_win_height))
			editor.debug_plugin_message(log.format("tabwin height   = %s", tabwin_height))
			editor.debug_plugin_message(log.format("tabwin width = %s", tabwin_width))

		self._tabwin.set_size_request(tabwin_width, tabwin_height)

		self._tabwin_resize_id = None

		return False

