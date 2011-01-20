#!/usr/bin/env python
# encoding: utf-8
# vim: ts=4 noexpandtab

from __future__ import print_function
from routing import Mapper as mapper

mapper().connect('/:controller(/:action(/:id)(.:format))')
print(mapper()._routes[0].urlize(controller='test', action='index'))
