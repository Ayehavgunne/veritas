# TODO: Add more sql types
class Type(object):
	def __repr__(self):
		return '{}()'.format(type(self.__name__))


class Serial(Type):
	def __str__(self):
		return 'SERIAL'


class Varchar(Type):
	def __init__(self, length=None):
		self.lenth = length

	def __str__(self):
		if self.lenth:
			return 'VARCHAR({})'.format(self.lenth)
		else:
			return 'VARCHAR'

	def __repr__(self):
		if self.lenth:
			return '{}(length={})'.format(type(self.__name__), self.lenth)
		else:
			return '{}()'.format(type(self.__name__))


class CharacterVarying(Varchar):
	def __init__(self):
		super().__init__()


class Integer(Type):
	def __str__(self):
		return 'INTEGER'


class BigInt(Type):
	def __str__(self):
		return 'BIGINT'


class Boolean(Type):
	def __str__(self):
		return 'BOOLEAN'


class Date(Type):
	def __str__(self):
		return 'DATE'


class Interval(Type):
	def __str__(self):
		return 'INTERVAL'


class Money(Type):
	def __str__(self):
		return 'MONEY'


class Numeric(Type):
	def __init__(self, precision=None, scale=None):
		self.precision = precision
		self.scale = scale

	def __str__(self):
		if self.precision and self.scale:
			return 'NUMERIC({}, {})'.format(self.precision, self.scale)
		elif self.precision:
			return 'NUMERIC({})'.format(self.precision)
		else:
			return 'NUMERIC'

	def __repr__(self):
		if self.precision and self.scale:
			return '{}(precision={}, scale={})'.format(type(self.__name__), self.precision, self.scale)
		elif self.precision:
			return '{}(precision={})'.format(type(self.__name__), self.precision)
		else:
			return '{}()'.format(type(self.__name__))


class Percent(Type):
	def __str__(self):
		return 'PERCENT'


class Time(Type):
	def __str__(self):
		return 'TIME WITHOUT TIMEZONE'


class Timestamp(Type):
	def __str__(self):
		return 'TIMESTAMP WITHOUT TIMEZONE'


class TimeTimezone(Type):
	def __str__(self):
		return 'TIME WITH TIMEZONE'


class TimestampTimezone(Type):
	def __str__(self):
		return 'TIMESTAMP WITH TIMEZONE'
