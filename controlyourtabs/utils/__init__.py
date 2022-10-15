# -*- coding: utf-8 -*-
#
# __init__.py
# This file is part of python-gtk-utils
#
# Copyright (C) 2013, 2017 Jeffery To <jeffery.to@gmail.com>
# https://github.com/jefferyto/python-gtk-utils
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

from gi.repository import GObject


# from future.utils

def _iteritems(obj, **kwargs):
	func = getattr(obj, 'iteritems', None)
	if not func:
		func = obj.items
	return func(**kwargs)


# signal handlers

def _get_handler_ids_name(ns):
	return ns.__class__.__name__ + 'HandlerIds'

def _get_handler_ids(ns, target):
	name = _get_handler_ids_name(ns)
	return getattr(target, name, [])

def _set_handler_ids(ns, target, ids):
	name = _get_handler_ids_name(ns)
	setattr(target, name, ids)

def _del_handler_ids(ns, target):
	name = _get_handler_ids_name(ns)
	if hasattr(target, name):
		delattr(target, name)

def connect_handlers(ns, target, signals, prefix_or_fn, *args):
	handler_ids = _get_handler_ids(ns, target)

	for signal in signals:
		if hasattr(prefix_or_fn, '__call__'):
			fn = prefix_or_fn
		else:
			fn = getattr(ns, 'on_%s_%s' % (prefix_or_fn, to_name(signal)))

		handler_ids.append(target.connect(signal, fn, *args))

	_set_handler_ids(ns, target, handler_ids)

def disconnect_handlers(ns, target):
	for handler_id in _get_handler_ids(ns, target):
		target.disconnect(handler_id)

	_del_handler_ids(ns, target)

def block_handlers(ns, target):
	for handler_id in _get_handler_ids(ns, target):
		target.handler_block(handler_id)

def unblock_handlers(ns, target):
	for handler_id in _get_handler_ids(ns, target):
		target.handler_unblock(handler_id)


# bindings

def _get_bindings_name(ns):
	return ns.__class__.__name__ + 'Bindings'

def _get_bindings(ns, source, target):
	name = _get_bindings_name(ns)
	binding_map = getattr(source, name, {})
	return binding_map[target] if target in binding_map else []

def _set_bindings(ns, source, target, bindings):
	name = _get_bindings_name(ns)
	binding_map = getattr(source, name, {})
	binding_map[target] = bindings
	setattr(source, name, binding_map)

def _del_bindings(ns, source, target):
	name = _get_bindings_name(ns)
	binding_map = getattr(source, name, {})
	if target in binding_map:
		del binding_map[target]
	if not binding_map and hasattr(source, name):
		delattr(source, name)

def create_bindings(ns, source, target, properties, *args):
	bindings = _get_bindings(ns, source, target)

	if isinstance(properties, dict):
		for (source_property, target_property) in _iteritems(properties):
			binding = source.bind_property(
				source_property,
				target, target_property,
				*args
			)
			bindings.append(binding)

	else:
		for prop in properties:
			binding = source.bind_property(
				prop,
				target, prop,
				flags,
				transform_to, transform_from, user_data
			)
			bindings.append(binding)

	_set_bindings(ns, source, target, bindings)

def release_bindings(ns, source, target):
	for binding in _get_bindings(ns, source, target):
		GObject.Binding.unbind(binding)

	_del_bindings(ns, source, target)


# misc

def to_name(value):
	return str(value).replace('-', '_').replace('::', '_')

def debug_str(value):
	if isinstance(value, GObject.Object):
		# hash(value) is the memory address of the underlying gobject
		result = value.__gtype__.name + ': ' + hex(hash(value))
	else:
		result = value

	return result

