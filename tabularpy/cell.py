import locale
from . import Settings
from . import tables
from . import row
from . import col

locale.setlocale(locale.LC_ALL, '')


class Cell(object):
	__slots__ = ('value', 'header', 'row_num', 'col_num', '_parent', '_settings', '_i')

	def __init__(self, value, header=None, row_num=None, col_num=None, parent=None, settings=Settings()):
		self.header = header
		self.row_num = row_num
		self.col_num = col_num
		self._parent = parent
		self._settings = settings
		self.value = value
		self._i = 0

	@property
	def column_type(self):
		if isinstance(self._parent, row.Row):
			return self._parent.column_types
		elif isinstance(self._parent, col.Col):
			return self._parent.column_type
		elif isinstance(self._parent, tables.BaseTable):
			return self._parent.column_types[self.col_num]

	def replace(self, old, new):
		if isinstance(self.value, str):
			return self._new(self.value.replace(old, new))

	def _new(self, value):
		return Cell(value, self.header, self.row_num, self.col_num, self._parent, self._settings)

	def __setattr__(self, key, value):
		if key == 'value':
			if self._parent:
				if isinstance(self._parent, row.Row):
					self._parent[self.header] = value
				elif isinstance(self._parent, col.Col):
					self._parent[self.row_num] = value
				elif isinstance(self._parent, tables.BaseTable):
					self._parent[self.header][self.row_num] = value
		object.__setattr__(self, key, value)

	def __eq__(self, other):
		if isinstance(other, Cell):
			return self.value == other.value
		else:
			return self.value == other

	def __ne__(self, other):
		return not self.__eq__(other)

	def __lt__(self, other):
		if isinstance(other, Cell):
			return self.value < other.value
		else:
			return self.value < other

	def __le__(self, other):
		if isinstance(other, Cell):
			return self.value <= other.value
		else:
			return self.value <= other

	def __gt__(self, other):
		if isinstance(other, Cell):
			return self.value > other.value
		else:
			return self.value > other

	def __ge__(self, other):
		if isinstance(other, Cell):
			return self.value >= other.value
		else:
			return self.value >= other

	def __bool__(self):
		return bool(self.value)

	def __add__(self, other):
		if isinstance(other, Cell):
			return self._new(self.value + other.value)
		else:
			return self._new(self.value + other)

	def __sub__(self, other):
		if isinstance(other, Cell):
			return self._new(self.value - other.value)
		else:
			return self._new(self.value - other)

	def __mul__(self, other):
		if isinstance(other, Cell):
			return self._new(self.value * other.value)
		else:
			return self._new(self.value * other)

	def __floordiv__(self, other):
		if isinstance(other, Cell):
			return self._new(self.value // other.value)
		else:
			return self._new(self.value // other)

	def __truediv__(self, other):
		if isinstance(other, Cell):
			return self._new(self.value / other.value)
		else:
			return self._new(self.value / other)

	def __mod__(self, other):
		if isinstance(other, Cell):
			return self._new(self.value % other.value)
		else:
			return self._new(self.value % other)

	def __pow__(self, other):
		if isinstance(other, Cell):
			return self._new(self.value ** other.value)
		else:
			return self._new(self.value ** other)

	def __and__(self, other):
		if isinstance(other, Cell):
			return self._new(self.value & other.value)
		else:
			return self._new(self.value & other)

	def __xor__(self, other):
		if isinstance(other, Cell):
			return self._new(self.value ^ other.value)
		else:
			return self._new(self.value ^ other)

	def __or__(self, other):
		if isinstance(other, Cell):
			return self._new(self.value | other.value)
		else:
			return self._new(self.value | other)

	def __iadd__(self, other):
		if isinstance(other, Cell):
			self.value += other.value
		else:
			self.value += other
		return self

	def __isub__(self, other):
		if isinstance(other, Cell):
			self.value -= other.value
		else:
			self.value -= other
		return self

	def __imul__(self, other):
		if isinstance(other, Cell):
			self.value *= other.value
		else:
			self.value *= other
		return self

	def __idiv__(self, other):
		if isinstance(other, Cell):
			self.value /= other.value
		else:
			self.value /= other
		return self

	def __ifloordiv__(self, other):
		if isinstance(other, Cell):
			self.value //= other.value
		else:
			self.value //= other
		return self

	def __imod__(self, other):
		if isinstance(other, Cell):
			self.value %= other.value
		else:
			self.value %= other
		return self

	def __ipow__(self, other):
		if isinstance(other, Cell):
			self.value **= other.value
		else:
			self.value **= other
		return self

	def __pos__(self):
		return self._new(+self.value)

	def __neg__(self):
		return self._new(-self.value)

	def __abs__(self):
		return self._new(abs(self.value))

	def __invert__(self):
		return self._new(~self.value)

	def __int__(self):
		return int(self.value)

	def __float__(self):
		return float(self.value)

	def __oct__(self):
		return oct(self.value)

	def __hex__(self):
		return hex(self.value)

	def __round__(self, n=None):
		return self._new(round(self.value, n))

	def __ceil__(self):
		from math import ceil
		return self._new(ceil(self.value))

	def __floor__(self):
		from math import floor
		return self._new(floor(self.value))

	def __trunc__(self):
		from math import trunc
		return self._new(trunc(self.value))

	def __iter__(self):
		if isinstance(self.value, str):
			return self
		else:
			return NotImplemented

	def __next__(self):
		if isinstance(self.value, str):
			if self._i < len(self.value):
				val = self.value[self._i]
				self._i += 1
				return val
			else:
				self._i = 0
				raise StopIteration
		else:
			return NotImplemented

	def __len__(self):
		return len(self.value)

	def __repr__(self):
		return '{}({}, {}, {}, {})'.format(self.__class__.__name__, self.value, self.header, self.row_num,
			self.col_num)

	def __str__(self):
		return str(self.value)

	def __hash__(self):
		return hash(repr(self.value))
