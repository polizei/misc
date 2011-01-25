#!/usr/bin/env python
# encoding: utf-8
# vim: ts=4 noexpandtab

from __future__ import print_function
from routing import Mapper as m

m.root(controller='home', action='index')
m.connect('/whatever/suites/best.:format', controller='whatever', action='fuck', id=123)
m.connect('/:controller(/:action(/:id)(.:format))', defaults=dict(action='index', format='html'))

#print(m.parameterize('/foo/bar/123.js'))
#print()

print(m.urlize(controller='home', action='index', lang='en'))
print(m.urlize(controller='whatever', action='fuck', id=123, format='xml'))
print(m.urlize(controller='whatever', action='fuck', id=456, format='xml'))
