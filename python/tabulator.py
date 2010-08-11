# encoding: utf-8
# vim: ts=4 noexpandtab

class Tabulator:
	'''Table stringifier. Prints tables just like MySQL's console'''

	def __init__(self, columns=[], names=[], data=[]):
		'''Constructor. Initializes default values'''

		self.columns	= columns
		self.names		= names
		self.data		= data

	def add_column(self, column, name):
		'''Adds a column to be printed'''

		self.columns.append(column)
		self.names.append(name)

	def set_data(self, data):
		'''Sets the data array to be printed'''

		self.data = data

	def __str__(self):
		'''Returns string representation of the table'''

		r = ''

		# calculate maximum lengths
		lengths = []
		for x in range(0, len(self.columns)):
			l = len(self.names[x])
			for y in range(0, len(self.data)):
				try:
					exec 'v = self.data[y].' + self.columns[x]
				except:
					v = ''

				l = max(l, len(v))

			lengths.append(l)

		# print top border
		r += '+'
		for x in range(0, len(lengths)):
			r += '-' * lengths[x]
			r += '--+'
		r += '\n'

		# print column names
		r += '|'
		for x in range(0, len(self.names)):
			r += ' '
			r += self.names[x]
			r += ' ' * (lengths[x] - len(self.names[x]))
			r += ' |'
		r += '\n'

		# print middle border
		r += '+'
		for x in range(0, len(lengths)):
			r += '-' * lengths[x]
			r += '--+'
		r += '\n'

		# print data
		for x in range(0, len(self.data)):
			r += '|'
			for y in range(0, len(self.columns)):
				try:

					exec 'v = self.data[x].' + self.columns[y]
				except:
					v = ''

				r += ' '
				r += v
				r += ' ' * (lengths[y] - len(v))
				r += ' |'

			r += '\n'

		# print bottom border
		r += '+'
		for x in range(0, len(lengths)):
			r += '-' * lengths[x]
			r += '--+'
		r += '\n'

		return r
