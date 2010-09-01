#!/usr/bin/env python

from tabulator import Tabulator

class Foo:
	def __init__(self, name, dob, comment):
		self.name		= name
		self.dob		= dob
		self.comment	= comment

data = [
	Foo('Latchezar Tzvetkoff', '1987-01-07', 'I\'m a bad ass mother fucker, mother fucker!'),
	Foo('Foobar Blahbleh', '1987-12-12', 'Foobar Blahbleh is just another Lorem Ipsum...'),
	Foo('Jack overflow', '1980-12-26', 'Mona Lisa Harddrive'),
]

t = Tabulator()
t.add_column('name', 'Name')
t.add_column('dob', 'Date of birth')
t.add_column('comment', 'Comment')

t.set_data(data)
print t
