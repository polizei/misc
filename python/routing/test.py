#!/usr/bin/env python
# encoding: utf-8
# vim: ts=4 noexpandtab

from __future__ import print_function
from routing import Mapper

map = Mapper()

map.root(controller='home', action='index')
map.connect('/whatever/suites/best.:format', map=dict(controller='whatever', action='fuck', id='123'))
map.connect('/:controller(/:action(/:id)(.:format))', defaults=dict(action='index', format='html'))

print(map.parameterize('/foo/bar/123.js'))
print()

print(map.urlize(controller='home', action='index'))
print(map.urlize(controller='news', action='view', id='123', format='xml', cache='0'))
