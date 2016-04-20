from . import operators
from . import types
from .conditions import Condition


# TODO: Add alter column statements
class Column(object):
	def __init__(self, name, type_, parent=None, database=None, primary_key=False,
			index=False, unique=False, nullable=True, default=None):
		self.name = name
		self.database = database
		if isinstance(type_, int):
			if type_ == 21 or type_ == 23:
				type_ = 'INTEGER'
			elif type_ == 20:
				type_ = 'BIGINT'
			elif type_ == 16:
				type_ = 'BOOLEAN'
			elif type_ == 1082:
				type_ = 'DATE'
			elif type_ == 700 or type_ == 701 or type_ == 1700:
				type_ = 'NUMERIC'
			elif type_ == 2281 or type_ == 1186:
				type_ = 'INTERVAL'
			elif type_ == 790:
				type_ = 'MONEY'
			elif type_ == 109164:
				type_ = 'PERCENT'
			elif type_ == 25 or type_ == 1043:
				type_ = 'VARCHAR'
			elif type_ == 1083 or type_ == 1266:
				type_ = 'TIME'
			elif type_ == 11605 or type_ == 1114 or type_ == 1184:
				type_ = 'TIMESTAMP'
		self.type_ = type_
		self.primary_key = primary_key
		self.serial = None
		self.serial_val = 1
		self.index = index
		self.unique = unique
		self.nullable = nullable
		self.default = default
		self.parent = parent
		self.quote = True if isinstance(type_, (
			types.Varchar,
			types.Time,
			types.Timestamp,
			types.Date,
			types.Interval
		)) else False
		self._ignore = False

	def __add__(self, other):
		if other is None:
			raise ValueError("unsuported operand type(s) for +: '{}' and 'NoneType'".format(type(self)))
		return Condition(self, operators.Add(other, self.quote))

	def __sub__(self, other):
		if other is None:
			raise ValueError("unsuported operand type(s) for -: '{}' and 'NoneType'".format(type(self)))
		return Condition(self, operators.Subtract(other, self.quote))

	def __mul__(self, other):
		if other is None:
			raise ValueError("unsuported operand type(s) for *: '{}' and 'NoneType'".format(type(self)))
		return Condition(self, operators.Multiply(other, self.quote))

	def __truediv__(self, other):
		if other is None:
			raise ValueError("unsuported operand type(s) for /: '{}' and 'NoneType'".format(type(self)))
		return Condition(self, operators.Divide(other, self.quote))

	def __mod__(self, other):
		if other is None:
			raise ValueError("unsuported operand type(s) for %: '{}' and 'NoneType'".format(type(self)))
		return Condition(self, operators.Mod(other, self.quote))

	def __eq__(self, other):
		if other is None:
			return Condition(self, operators.Is(types.Null))
		else:
			return Condition(self, operators.Equals(other, self.quote))

	def __ne__(self, other):
		if other is None:
			return Condition(self, operators.Not(operators.Is(other)))
		else:
			return Condition(self, operators.NotEquals(other, self.quote))

	def __lt__(self, other):
		return Condition(self, operators.LessThan(other, self.quote))

	def __gt__(self, other):
		return Condition(self, operators.GreaterThan(other, self.quote))

	def __le__(self, other):
		return Condition(self, operators.LessThanEquals(other, self.quote))

	def __ge__(self, other):
		return Condition(self, operators.GreaterThanEquals(other, self.quote))

	def is_true(self):
		if isinstance(self.type_, types.Boolean):
			return Condition(self, operators.Is(True))
		else:
			raise ValueError("'IS TRUE' expression can only be used with Booleans")

	def is_false(self):
		if isinstance(self.type_, types.Boolean):
			return Condition(self, operators.Is(False))
		else:
			raise ValueError("'IS FALSE' expression can only be used with Booleans")

	def between(self, a, b):
		return Condition(self, operators.Between(a, b))

	def not_between(self, a, b):
		return Condition(self, operators.Not(operators.Between(a, b)))

	def is_null(self):
		return Condition(self, operators.Is(types.Null))

	def is_not_null(self):
		return Condition(self, operators.Not(types.Null))

	def like(self, what):
		return Condition(self, operators.Like(what))

	def not_like(self, what):
		return Condition(self, operators.Not(operators.Like(what)))

	def in_(self, *iterable):
		return Condition(self, operators.In(iterable, self.quote))

	def as_(self, label):
		pass

	def change_type(self, type_):
		self.type_ = type_
		if self.parent.data:
			self.parent.data.column_types[self.name] = str(type_)

	def desc(self):
		return operators.Desc(self)

	def ignore(self, undo=False):
		if undo:
			self._ignore = False
		else:
			self._ignore = True

	def __str__(self):
		string = '{} {}'.format(self.name, self.type_)
		if not self.nullable:
			string = '{} NOT NULL'.format(string)
		if self.default:
			string = '{} DEFAULT {}'.format(string, self.default)
		return string

	def __repr__(self):
		return 'Column(name={}, type_={})'.format(self.name, self.type_)
