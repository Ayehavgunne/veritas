from decimal import Decimal
from . import Settings
from .cells import get_cell_of_type
from .cells import BaseCell
from .cells import StrCell


class Col(object):
	__slots__ = ('cells', 'labels', 'column_type', 'header', 'col_num', '_parent', '_i', '_settings')

	def __init__(self, cells, labels, column_type, header, col_num, parent, settings=Settings()):
		self.cells = cells
		self.labels = labels
		self.column_type = column_type
		self.header = header
		self.col_num = col_num
		self._parent = parent
		self._settings = settings
		self._i = 0

	def index(self, item):
		return self.cells.index(item)

	def to_dict(self):
		return {label: cell for label, cell in zip(self.labels, self.cells)}

	def to_list(self):
		return self.cells

	def keys(self):
		return self.labels

	def sum(self):
		return sum([Decimal(str(cell).replace(',', '')) for cell in self.cells if cell != '' and cell is not None])

	def get_cell(self, x):
		if isinstance(x, str):
			index = self.labels.index(x)
			cell_type = get_cell_of_type(self.column_type)
			if cell_type is None:
				return StrCell(self.cells[index], self.header, self.labels[index], index, self.col_num, self, self._settings)
			return cell_type(self.cells[index], self.header, self.labels[index], index, self.col_num, self, self._settings)
		elif isinstance(x, int):
			label = self.labels[x]
			cell_type = get_cell_of_type(self.column_type)
			if cell_type is None:
				return StrCell(self.cells[x], self.header, label, x, self.col_num, self, self._settings)
			return cell_type(self.cells[x], self.header, label, x, self.col_num, self, self._settings)

	def to_html(self, add_attr=None, row_total=False):
		if add_attr:
			html = ''.join(['<td {}>{}</td>'.format(add_attr(cell, self.column_types[self.labels[x]], self.labels[x], self), self.get_cell(x)) for x, cell in enumerate(self.cells)])
		else:
			html = ''.join(['<td>{}</td>'.format(cell) for cell in self.cells])
		if row_total:
			html = '{}<td class="rowtotal">{:,}</td>'.format(html, self.sum())
		return html

	def __next__(self):
		if self._i < len(self.cells):
			cell = self.get_cell(self._i)
			self._i += 1
			return cell
		else:
			self._i = 0
			raise StopIteration

	def __getattr__(self, item):
		if item in self.labels:
			idx = self.labels.index(item)
			return self.get_cell(idx)
		raise AttributeError('attribute {} does not exist'.format(item))

	def __getitem__(self, item):
		if isinstance(item, str):
			if item in self.labels:
				idx = self.labels.index(item)
				return self.get_cell(idx)
		elif isinstance(item, int):
			return self.get_cell(item)
		raise AttributeError('{} does not have item of {}'.format(self, item))

	def __setitem__(self, key, value):
		if isinstance(key, BaseCell):
			key = key.value
		if isinstance(value, BaseCell):
			value = value.value
		if isinstance(key, int):
			if key < len(self.cells):
				self.cells[key] = value
				if self._parent:
					self._parent.change_cell(self.header, key, value)
			else:
				raise IndexError('assignment index out of range')
		elif isinstance(key, str):
			if key in self.labels:
				self.cells[self.labels.index(key)] = value
				if self._parent:
					self._parent.change_cell(key, self.labels.index(key), value)
			else:
				raise KeyError("'{}'".format(key))
		else:
			raise TypeError('indices must be integers or strings, not {}'.format(type(key)))

	def __delitem__(self, item):
		if isinstance(item, str):
			if item in self.labels:
				del self.cells[self.labels.index(item)]
				del self.labels[self.labels.index(item)]
		elif isinstance(item, int):
			del self.labels[item]
			del self.cells[item]

	def __contains__(self, item):
		if isinstance(item, str):
			if item in self.labels:
				return True
			else:
				return False
		elif isinstance(item, int):
			if item in self.cells:
				return True
			else:
				return False

	def __eq__(self, other):
		if self.cells != other.cells:
			return False
		if self.labels != other.labels:
			return False
		return True

	def __len__(self):
		return len(self.cells)

	def __str__(self):
		return str(self.cells)

	def __repr__(self):
		return '<{} Cells: {}>'.format(type(self).__name__, self.cells)
