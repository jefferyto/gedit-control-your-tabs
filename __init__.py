# -*- coding: utf-8 -*-
#
# __init__.py
# This file is part of python-gtk-utils
#
# Copyright (C) 2013 Jeffery To <jeffery.to@gmail.com>
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

def _get_handler_ids_name(ns):
	return ns.__class__.__name__ + 'HandlerIds'

def _get_handler_ids(ns, target):
	name = _get_handler_ids_name(ns)
	return getattr(target, name) if hasattr(target, name) else []

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
			fn = getattr(ns, 'on_%s_%s' % (prefix_or_fn, signal.replace('-', '_').replace('::', '_')))
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
