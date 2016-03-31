from .operators import In
from .types import Boolean
from .types import Varchar
from .types import Date
from .types import Time
from .types import Timestamp
from .conditions import Condition


# TODO: Add alter column statements
class Column(object):
	def __init__(self, name, type_, parent=None, database=None, primary_key=False,
			index=False, unique=False, nullable=True, default=None):
		self.name = name
		self.type_ = type_
		self.primary_key = primary_key
		self.serial = None
		self.serial_val = 1
		self.index = index
		self.unique = unique
		self.nullable = nullable
		self.default = default
		self.descending = False
		self.parent = parent
		self.database = database
		self._ignore = False
	# TODO: Add more Condition Operators

	def __eq__(self, other):
		if other is None:
			return Condition('{} IS NULL'.format(self.name), self)
		else:
			return Condition(self._operation(other, '='), self)

	def __ne__(self, other):
		if other is None:
			return Condition('{} IS NOT NULL'.format(self.name), self)
		else:
			return Condition(self._operation(other, '!='), self)

	def __lt__(self, other):
		return Condition(self._operation(other, '<'), self)

	def __gt__(self, other):
		return Condition(self._operation(other, '>'), self)

	def __le__(self, other):
		return Condition(self._operation(other, '<='), self)

	def __ge__(self, other):
		return Condition(self._operation(other, '>='), self)

	def is_true(self):
		if isinstance(self.type_, Boolean):
			return Condition('{} IS TRUE'.format(self.name), self)
		else:
			raise ValueError("'IS TRUE' expression can only be used with Booleans")

	def is_false(self):
		if isinstance(self.type_, Boolean):
			return Condition('{} IS FALSE'.format(self.name), self)
		else:
			raise ValueError("'IS FALSE' expression can only be used with Booleans")

	def between(self, a, b):
		if isinstance(self.type_, (Varchar, Date, Time, Timestamp)):
			return Condition("{} BETWEEN {} AND '{}'".format(self.name, a, b), self)
		else:
			return Condition('{} BETWEEN {} AND {}'.format(self.name, a, b), self)

	def not_between(self, a, b):
		if isinstance(self.type_, (Varchar, Date, Time, Timestamp)):
			return Condition("{} NOT BETWEEN {} AND '{}'".format(self.name, a, b), self)
		else:
			return Condition('{} NOT BETWEEN {} AND {}'.format(self.name, a, b), self)

	def is_null(self):
		return Condition('{} IS NULL'.format(self.name), self)

	def is_not_null(self):
		return Condition('{} IS NOT NULL'.format(self.name), self)

	def like(self, what):
		return Condition('{} IS LIKE {}'.format(self.name, what), self)

	def not_like(self, what):
		return Condition('{} IS NOT LIKE {}'.format(self.name, what), self)

	def in_(self, iterable):
		return '{} {}'.format(self.name, In(iterable))

	def change_type(self, type_):
		self.type_ = type_
		if self.parent.data:
			self.parent.data.column_types[self.name] = str(type_)

	def desc(self):
		self.descending = True
		return self

	def ignore(self, undo=False):
		if undo:
			self._ignore = False
		else:
			self._ignore = True

	def _operation(self, other, operator):
		if isinstance(other, Column):
			return '{} {} {}'.format(self.name, operator, other.name)
		elif isinstance(self.type_, (Varchar, Date, Time, Timestamp)):
			return "{} {} '{}'".format(self.name, operator, other)
		else:
			return '{} {} {}'.format(self.name, operator, other)

	def __str__(self):
		string = '{} {}'.format(self.name, self.type_)
		if not self.nullable:
			string = '{} NOT NULL'.format(string)
		if self.default:
			string = '{} DEFAULT {}'.format(string, self.default)
		return string

	def __repr__(self):
		return 'Column(name={}, type_={})'.format(self.name, self.type_)
