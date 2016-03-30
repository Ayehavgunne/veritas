import locale
from abc import ABCMeta
from abc import abstractclassmethod
from decimal import Decimal
from decimal import InvalidOperation
from datetime import datetime
from datetime import date
from datetime import time
from datetime import timedelta
from . import default_settings
from .util import datetime_to_quarter
from .util import seconds_since_epoch
from .util import parse_time_delta
from .util import parse_date_time_string

locale.setlocale(locale.LC_ALL, '')


def get_cell_of_type(type_desc):
	if type_desc:
		type_desc = str(type_desc).lower()
		if type_desc == 'string' or type_desc == 'varchar':
			return StrCell
		elif type_desc == 'integer':
			return IntCell
		elif type_desc == 'float':
			return FloatCell
		elif type_desc == 'decimal' or type_desc == 'numeric':
			return DecimalCell
		elif type_desc == 'percent':
			return PercentCell
		elif type_desc == 'money':
			return MoneyCell
		elif type_desc == 'bool':
			return BooleanCell
		elif type_desc == 'date':
			return DateCell
		elif type_desc == 'time':
			return TimeCell
		elif type_desc == 'seconds':
			return SecondsCell
		elif type_desc == 'timestamp':
			return TimestampCell
		elif type_desc == 'interval':
			return IntervalCell


class BaseCell(metaclass=ABCMeta):
	__slots__ = ('_base', 'value', 'header', 'label', 'column_type', 'row_num', 'col_num', '_parent', '_settings', 'getquoted')

	def __init__(self, base, value, header=None, label=None, column_type='string', row_num=None, col_num=None, parent=None, settings=default_settings):
		self._base = base
		self.header = header
		self.label = label
		self.column_type = column_type
		self.row_num = row_num
		self.col_num = col_num
		self._parent = parent
		self._settings = settings
		if value is None:
			self.value = value
		elif self._base is not str and value == '':
			self.value = None
		else:
			if self._base is date:
				self.value = self._base(value.year, value.month, value.day)
			elif self._base is time:
				self.value = self._base(value.hour, value.minute, value.second, value.microsecond, value.tzinfo)
			elif self._base is datetime:
				self.value = self._base(value.year, value.month, value.day, value.hour, value.minute, value.second, value.microsecond, value.tzinfo)
			elif self._base is timedelta:
				if hasattr(value, 'milliseconds'):
					self.value = self._base(value.days, value.seconds, value.microseconds, value.milliseconds, value.minutes, value.hours, value.weeks)
				else:
					self.value = self._base(value.days, value.seconds, value.microseconds)
			elif self._base is int:
				if isinstance(value, str):
					value = value.replace(',', '')
				if value == 'None':
					self.value = None
				else:
					self.value = self._base(value)
			elif self._base is Decimal:
				value = str(value)
				if value == 'None':
					self.value = None
				else:
					if '$' in value:
						value = value.replace('$', '')
					if '%' in value:
						value = value.replace('%', '')
					if ',' in value:
						value = value.replace(',', '')
					self.value = self._base(value)
			else:
				if self._base is float:
					if isinstance(value, str):
						value = value.replace(',', '')
				try:
					self.value = self._base(value)
				except InvalidOperation:
					print(value)

	def __setattr__(self, key, value):
		if key == 'value':
			if self._parent:
				if 'Row' in self._parent.__class__.__name__:
					self._parent[self.header] = value
				else:
					self._parent[self.row_num] = value
		object.__setattr__(self, key, value)

	def _new(self, value, class_type=None):
		if class_type is None:
			if isinstance(value, str):
				return StrCell(value, self.header, self.label, self.row_num, self.col_num)
			elif isinstance(value, int):
				return IntCell(value, self.header, self.label, self.row_num, self.col_num)
			elif isinstance(value, float):
				return FloatCell(value, self.header, self.label, self.row_num, self.col_num)
			elif isinstance(value, Decimal):
				return DecimalCell(value, self.header, self.label, self.row_num, self.col_num)
			elif isinstance(value, bool):
				return BooleanCell(value, self.header, self.label, self.row_num, self.col_num)
			elif isinstance(value, date):
				return DateCell(value, self.header, self.label, self.row_num, self.col_num)
			elif isinstance(value, time):
				return TimeCell(value, self.header, self.label, self.row_num, self.col_num)
			elif isinstance(value, datetime):
				return TimestampCell(value, self.header, self.label, self.row_num, self.col_num)
			elif isinstance(value, timedelta):
				return IntervalCell(value, self.header, self.label, self.row_num, self.col_num)
			else:
				return self.__class__(value, self.header, self.label, self.row_num, self.col_num)
		else:
			return class_type(value, self.header, self.label, self.row_num, self.col_num)

	def change_type(self, class_type):
		if self._is_of_same_base_type(class_type):
			return self._new(self.value, class_type)
		else:
			raise TypeError('cannot create instance of type {}'.format(class_type))

	@staticmethod
	def _is_of_same_base_type(other):
		return isinstance(other, BaseCell)

	def __eq__(self, other):
		if self.value is not None:
			if self._is_of_same_base_type(other):
				return self.value == other.value
			else:
				return self._base.__eq__(self.value, other)
		else:
			if self._is_of_same_base_type(other):
				return self.value == other.value
			else:
				return self.value == other

	def __ne__(self, other):
		if self.value is not None:
			if self._is_of_same_base_type(other):
				return self.value != other.value
			else:
				return self._base.__ne__(self.value, other)
		else:
			if self._is_of_same_base_type(other):
				return self.value != other.value
			else:
				return self.value != other

	def __repr__(self):
		return '{}({}, {}, {}, {}, {}, {})'.format(self.__class__.__name__, self.value, self.header, self.label, self.row_num, self.col_num, self._parent)

	def __str__(self):
		if self.value is not None:
			return str(self.value)
		else:
			return 'None'

	@abstractclassmethod
	def is_numeric(self):
		pass


class StrCell(BaseCell):
	__slots__ = ('_i',)

	def __init__(self, value, header=None, label=None, row_num=None, col_num=None, parent=None, settings=default_settings):
		super().__init__(str, value, header, label, 'string', row_num, col_num, parent, settings)
		self._i = 0

	def __add__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(self.value + other.value)
			else:
				return self._new(self._base.__add__(self.value, other))

	def __contains__(self, item):
		if self.value is None and self._settings.ignore_none:
			return False
		else:
			if self._is_of_same_base_type(item):
				return item.value in self.value
			else:
				return self._base.__contains__(self.value, item)

	def __float__(self):
		if self.value is None and self._settings.ignore_none:
			return None
		else:
			return float(self.value)

	def __ge__(self, other):
		if self.value is None and self._settings.ignore_none:
			return False
		else:
			if self._is_of_same_base_type(other):
				return self.value >= other.value
			else:
				return self._base.__ge__(self.value, other)

	def __getitem__(self, item):
		if item < len(self.value):
			return self.value[item]
		else:
			raise IndexError('string index out of range')

	def __gt__(self, other):
		if self.value is None and self._settings.ignore_none:
			return False
		else:
			if self._is_of_same_base_type(other):
				return self.value > other.value
			else:
				return self._base.__gt__(self.value, other)

	def __iadd__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self
		else:
			if self._is_of_same_base_type(other):
				self.value = self.value + other.value
				return self._new(self.value)
			else:
				self.value = self.value + other
				return self._new(self.value)

	def __imul__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self
		else:
			if self._is_of_same_base_type(other):
				self.value = self.value * other.value
				return self
			else:
				self.value = self.value * other
				return self

	def __index__(self):
		if self.value is not None:
			return self.value
		else:
			raise TypeError('index cannot be of type \'NoneType\'')

	def __int__(self):
		if self.value is None and self._settings.ignore_none:
			return None
		else:
			return int(self.value)

	def __iter__(self):
		return self

	def __le__(self, other):
		if self.value is None and self._settings.ignore_none:
			return False
		else:
			if self._is_of_same_base_type(other):
				return self.value <= other.value
			else:
				return self._base.__le__(self.value, other)

	def __len__(self):
		if self.value is None and self._settings.ignore_none:
			return 0
		else:
			return self._base.__len__(self.value)

	def __lt__(self, other):
		if self.value is None and self._settings.ignore_none:
			return False
		else:
			if self._is_of_same_base_type(other):
				return self.value < other.value
			else:
				return self._base.__lt__(self.value, other)

	def __mod__(self):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			return self._base.__mod__(self.value)

	def __mul__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			return self._base.__mul__(self.value, other)

	def __next__(self):
		if self.value is None and self._settings.ignore_none:
			raise StopIteration
		else:
			if self._i < len(self.value):
				row = self.value[self._i]
				self._i += 1
				return row
			else:
				self._i = 0
				raise StopIteration

	def __rmod__(self):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			return self._base.__rmod__(self.value)

	def __rmul__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			return self._base.__rmul__(self.value, other)

	def capitalize(self):
		if self.value is not None:
			return self._new(self._base.capitalize(self.value))

	def casefold(self):
		if self.value is not None:
			return self._new(self._base.casefold(self.value))

	def center(self, width, fillchar=' '):
		if self.value is not None:
			self.value = self._base.center(self.value, width, fillchar)
			return self

	def count(self, sub, start=None, end=None):
		if self.value is not None:
			return self._base.count(self.value, sub, start, end)

	def encode(self, encoding='utf-8', errors='strict'):
		if self.value is not None:
			return self._base.encode(self.value, encoding, errors)

	def endswith(self, suffix, start=None, end=None):
		if self.value is not None:
			return self._base.endswith(self.value, suffix, start, end)

	def expandtabs(self, tabsize):
		if self.value is not None:
			return self._new(self._base.expandtabs(self.value, tabsize))

	def find(self, sub, start=None, end=None):
		if self.value is not None:
			return self._base.find(self.value, sub, start, end)

	def format(self, *args, **kwargs):
		if self.value is not None:
			self.value = self._base.format(self.value, *args, **kwargs)
			return self

	def format_map(self, mapping):
		if self.value is not None:
			self.value = self._base.format_map(self.value, mapping)
			return self

	def index(self, sub, start=None, end=None):
		if self.value is not None:
			return self._base.index(self.value, sub, start, end)

	def isalnum(self):
		if self.value is not None:
			return self._base.isalnum(self.value)

	def isalpha(self):
		if self.value is not None:
			return self._base.isalpha(self.value)

	def isdecimal(self):
		if self.value is not None:
			return self._base.isdecimal(self.value)

	def isdigit(self):
		if self.value is not None:
			return self._base.isdigit(self.value)

	def isidentifier(self):
		if self.value is not None:
			return self._base.isidentifier(self.value)

	def islower(self):
		if self.value is not None:
			return self._base.islower(self.value)

	def isnumeric(self):
		if self.value is not None:
			return self._base.isnumeric(self.value)

	def isprintable(self):
		if self.value is not None:
			return self._base.isprintable(self.value)

	def isspace(self):
		if self.value is not None:
			return self._base.isspace(self.value)

	def istitle(self):
		if self.value is not None:
			return self._base.istitle(self.value)

	def isupper(self):
		if self.value is not None:
			return self._base.isupper(self.value)

	def is_numeric(self):
		if self.value is not None:
			return True

	def join(self, iterable):
		if self.value is not None:
			return self._new(self._base.join(self.value, iterable))

	def ljust(self, width, fillchar=None):
		if self.value is not None:
			self.value = self._base.ljust(self.value, width, fillchar)
			return self

	def lower(self):
		if self.value is not None:
			return self._new(self._base.lower(self.value))

	def lstrip(self, chars=None):
		if self.value is not None:
			return self._new(self._base.lstrip(self.value, chars))

	def maketrans(self, *args, **kwargs):
		if self.value is not None:
			return self._base.maketrans(self.value, *args, **kwargs)

	def partition(self, sep):
		if self.value is not None:
			return self._base.partition(self.value, sep)

	def replace(self, old, new, count=-1):
		if self.value is not None:
			return self._new(self._base.replace(self.value, old, new, count))

	def rfind(self, sub, start=None, end=None):
		if self.value is not None:
			return self._base.rfind(self.value, sub, start, end)

	def rindex(self, sub, start=None, end=None):
		if self.value is not None:
			return self._base.rindex(self.value, sub, start, end)

	def rjust(self, width, fillchar=None):
		if self.value is not None:
			self.value = self._base.rjust(self.value, width, fillchar)
			return self

	def rpartition(self, sep):
		if self.value is not None:
			return self._base.rpartition(self.value, sep)

	def rsplit(self, sep=None, maxsplit=-1):
		if self.value is not None:
			return self._base.rsplit(self.value, sep, maxsplit)

	def rstrip(self, chars=None):
		if self.value is not None:
			return self._new(self._base.rstrip(self.value, chars))

	def split(self, sep=None, maxsplit=-1):
		if self.value is not None:
			return self._base.split(self.value, sep, maxsplit)

	def splitlines(self, keepends=None):
		if self.value is not None:
			return self._base.splitlines(self.value, keepends)

	def startswith(self, prefix, start=None, end=None):
		if self.value is not None:
			return self._base.startswith(self.value, prefix, start, end)

	def strip(self, chars=None):
		if self.value is not None:
			return self._new(self._base.strip(self.value, chars))

	def swapcase(self):
		if self.value is not None:
			return self._new(self._base.swapcase(self.value))

	def title(self):
		if self.value is not None:
			return self._new(self._base.title(self.value))

	def translate(self, table):
		if self.value is not None:
			return self._new(self._base.translate(self.value, table))

	def upper(self):
		if self.value is not None:
			return self._new(self._base.upper(self.value))

	def zfill(self, width):
		if self.value is not None:
			self.value = self._base.zfill(self.value, width)
			return self


class IntCell(BaseCell):
	__slots__ = ()

	def __init__(self, value, header=None, label=None, row_num=None, col_num=None, parent=None, settings=default_settings):
		super().__init__(int, value, header, label, 'integer', row_num, col_num, parent, settings)

	def __abs__(self):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			return self._new(self._base.__abs__(self.value))

	def __add__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(self.value + other.value)
			else:
				return self._new(self._base.__add__(self.value, other))

	def __and__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self.value & other.value
			else:
				return self._base.__and__(self.value, other)

	def __bool__(self):
		if self.value is not None:
			return self._base.__bool__(self.value)
		else:
			return False

	def __ceil__(self):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			return self._new(self._base.__ceil__(self.value))

	def __divmod__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return divmod(self.value, other.value)
			else:
				return self._new(self._base.__divmod__(self.value, other))

	def __float__(self):
		if self.value is None and self._settings.ignore_none:
			return None
		else:
			return self._base.__float__(self.value)

	def __floor__(self):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			return self._new(self._base.__floor__(self.value))

	def __floordiv__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(self.value // other.value)
			else:
				return self._new(self._base.__floordiv__(self.value, other))

	def __ge__(self, other):
		if self.value is None and self._settings.ignore_none:
			return False
		else:
			if self._is_of_same_base_type(other):
				return self.value >= other.value
			else:
				return self._base.__ge__(self.value, other)

	def __gt__(self, other):
		if self.value is None and self._settings.ignore_none:
			return False
		else:
			if self._is_of_same_base_type(other):
				return self.value > other.value
			else:
				return self._base.__gt__(self.value, other)

	def __iadd__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self
		else:
			if self._is_of_same_base_type(other):
				self.value = self.value + other.value
				return self._new(self.value)
			else:
				self.value = self.value + other
				return self._new(self.value)

	def __iand__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self
		else:
			if self._is_of_same_base_type(other):
				self.value = self.value & other.value
				return self._new(self.value)
			else:
				self.value = self.value & other
				return self._new(self.value)

	def __ifloordiv__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self
		else:
			if self._is_of_same_base_type(other):
				self.value = self.value // other.value
				return self._new(self.value)
			else:
				self.value = self.value // other
				return self._new(self.value)

	def __ilshift__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self
		else:
			if self._is_of_same_base_type(other):
				self.value = self.value << other.value
				return self._new(self.value)
			else:
				self.value = self.value << other
				return self._new(self.value)

	def __imod__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self
		else:
			if self._is_of_same_base_type(other):
				self.value = self.value % other.value
				return self._new(self.value)
			else:
				self.value = self.value % other
				return self._new(self.value)

	def __imul__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self
		else:
			if self._is_of_same_base_type(other):
				self.value = self.value * other.value
				return self._new(self.value)
			else:
				self.value = self.value * other
				return self._new(self.value)

	def __index__(self):
		if self.value is not None:
			return self.value
		else:
			raise TypeError('index cannot be of \'NoneType\'')

	def __int__(self):
		if self.value is None and self._settings.ignore_none:
			return None
		else:
			if self.value is not None:
				return self.value
			else:
				raise TypeError('int() argument must be a string, a bytes-like object or a number, not \'NoneType\'')

	def __invert__(self):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			return self._new(self._base.__invert__(self.value))

	def __ipow__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self
		else:
			if self._is_of_same_base_type(other):
				self.value = self.value ** other.value
				return self._new(self.value)
			else:
				self.value = self.value ** other
				return self._new(self.value)

	def __ior__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self
		else:
			if self._is_of_same_base_type(other):
				self.value = self.value | other.value
				return self._new(self.value)
			else:
				self.value = self.value | other
				return self._new(self.value)

	def __irshift__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self
		else:
			if self._is_of_same_base_type(other):
				self.value = self.value >> other.value
				return self._new(self.value)
			else:
				self.value = self.value >> other
				return self._new(self.value)

	def __isub__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self
		else:
			if self._is_of_same_base_type(other):
				self.value = self.value - other.value
				return self._new(self.value)
			else:
				self.value = self.value - other
				return self._new(self.value)

	def __itruediv__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self
		else:
			if self._is_of_same_base_type(other):
				self.value = self.value / other.value
				return self._new(self.value)
			else:
				self.value = self.value / other
				return self._new(self.value)

	def __ixor__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self
		else:
			if self._is_of_same_base_type(other):
				self.value = self.value ^ other.value
				return self._new(self.value)
			else:
				self.value = self.value ^ other
				return self._new(self.value)

	def __le__(self, other):
		if self.value is None and self._settings.ignore_none:
			return False
		else:
			if self._is_of_same_base_type(other):
				return self.value <= other.value
			else:
				return self._base.__le__(self.value, other)

	def __lshift__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(self.value << other.value)
			else:
				return self._new(self._base.__lshift__(self.value, other))

	def __lt__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self.value < other.value
			else:
				return self._base.__lt__(self.value, other)

	def __mod__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(self.value % other.value)
			else:
				return self._new(self._base.__mod__(self.value, other))

	def __mul__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(self.value * other.value)
			else:
				r = self._base.__mul__(self.value, other)
				if r is NotImplemented:
					r = self.value * other
				return self._new(r)

	def __neg__(self):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			return self._new(self._base.__neg__(self.value))

	def __or__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self.value | other.value
			else:
				return self._base.__or__(self.value, other)

	def __pos__(self):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			return self._new(self._base.__pos__(self.value))

	def __pow__(self, power, modulo=None):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(power):
				return self._new(pow(self.value, power.value, modulo))
			else:
				return self._new(self._base.__pow__(self.value, power, modulo))

	def __radd__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(other.value + self.value)
			else:
				return self._new(self._base.__radd__(self.value, other))

	def __rand__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return other.value & self.value
			else:
				return self._base.__rand__(self.value, other)

	def __rdivmod__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return divmod(other.value, self.value)
			else:
				return self._new(self._base.__rdivmod__(self.value, other))

	def __rfloordiv__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(other.value // self.value)
			else:
				return self._new(self._base.__rfloordiv__(self.value, other))

	def __rlshift__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(other.value << self.value)
			else:
				return self._new(self._base.__rlshift__(self.value, other))

	def __rmod__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(other.value % self.value)
			else:
				r = self._base.__rmod__(self.value, other)
				if r is NotImplemented:
					r = other * self.value
				return self._new(r)

	def __rmul__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(other.value * self.value)
			else:
				r = self._base.__rmul__(self.value, other)
				if r is NotImplemented:
					r = other * self.value
				return self._new(r)

	def __ror__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return other.value | self.value
			else:
				return self._base.__ror__(self.value, other)

	def __round__(self, n=None):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			return self._new(self._base.__round__(self.value, n))

	def __rpow__(self, power, modulo=None):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(power):
				return self._new(pow(power.value, self.value, modulo))
			else:
				return self._new(self._base.__rpow__(self.value, power))

	def __rrshift__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(other.value >> self.value)
			else:
				return self._new(self._base.__rrshift__(self.value, other))

	def __rshift__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(self.value >> other.value)
			else:
				return self._new(self._base.__rshift__(self.value, other))

	def __rsub__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(other.value - self.value)
			else:
				return self._new(self._base.__rsub__(self.value, other))

	def __rtruediv__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(other.value / self.value)
			else:
				return self._new(self._base.__rtruediv__(self.value, other))

	def __rxor__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(other.value ^ self.value)
			else:
				return self._new(self._base.__rxor__(self.value, other))

	def __str__(self):
		if self.value is not None:
			if self._settings.int_comma and self.header not in self._settings.dont_format:
				return '{:,}'.format(self.value)
			else:
				return str(self.value)
		else:
			return 'None'

	def __sub__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(self.value - other.value)
			else:
				return self._new(self._base.__sub__(self.value, other))

	def __truediv__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(self.value / other.value)
			else:
				return self._new(self._base.__truediv__(self.value, other))

	def __trunc__(self):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			return self._new(self._base.__trunc__(self.value))

	def __xor__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(self.value ^ other.value)
			else:
				return self._new(self._base.__xor__(self.value, other))

	@property
	def bitlength(self):
		if self.value is not None:
			return self._base.bit_length(self.value)

	def conjugate(self):
		if self.value is not None:
			return self._base.conjugate(self.value)

	@property
	def denominator(self):
		if self.value is not None:
			return self._base(self.value).denominator

	@property
	def imag(self):
		if self.value is not None:
			return self._base(self.value).imag

	def is_numeric(self):
		if self.value is not None:
			return True

	@property
	def numerator(self):
		if self.value is not None:
			return self._base(self.value).numerator

	@property
	def real(self):
		if self.value is not None:
			return self._base(self.value).real

	def to_bytes(self, length, byteorder):
		if self.value is not None:
			return self._base.to_bytes(self.value, length, byteorder)


class FloatCell(BaseCell):
	__slots__ = ()

	def __init__(self, value, header=None, label=None, row_num=None, col_num=None, parent=None, settings=default_settings):
		super().__init__(float, value, header, label, 'float', row_num, col_num, parent, settings)

	def __abs__(self):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			return self._new(self._base.__abs__(self.value))

	def __add__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(self.value + other.value)
			else:
				return self._new(self._base.__add__(self.value, other))

	def __bool__(self):
		if self.value is not None:
			return self._base.__bool__(self.value)
		else:
			return False

	def __divmod__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return divmod(self.value, other.value)
			else:
				return self._new(self._base.__divmod__(self.value, other))

	def __float__(self):
		if self.value is None and self._settings.ignore_none:
			return None
		else:
			if self.value is not None:
				return self.value
			else:
				raise TypeError('float() argument must be a string or a number, not \'NoneType\'')

	def __floordiv__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(self.value // other.value)
			else:
				return self._new(self._base.__floordiv__(self.value, other))

	def __ge__(self, other):
		if self.value is None and self._settings.ignore_none:
			return False
		else:
			if self._is_of_same_base_type(other):
				return self.value >= other.value
			else:
				return self._base.__ge__(self.value, other)

	def __gt__(self, other):
		if self.value is None and self._settings.ignore_none:
			return False
		else:
			if self._is_of_same_base_type(other):
				return self.value > other.value
			else:
				return self._base.__gt__(self.value, other)

	def __iadd__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self
		else:
			if self._is_of_same_base_type(other):
				self.value = self.value + other.value
				return self._new(self.value)
			else:
				self.value = self.value + other
				return self._new(self.value)

	def __ifloordiv__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self
		else:
			if self._is_of_same_base_type(other):
				self.value = self.value // other.value
				return self._new(self.value)
			else:
				self.value = self.value // other
				return self._new(self.value)

	def __imod__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self
		else:
			if self._is_of_same_base_type(other):
				self.value = self.value % other.value
				return self._new(self.value)
			else:
				self.value = self.value % other
				return self._new(self.value)

	def __imul__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self
		else:
			if self._is_of_same_base_type(other):
				self.value = self.value * other.value
				return self._new(self.value)
			else:
				self.value = self.value * other
				return self._new(self.value)

	def __index__(self):
		if self.value is not None:
			return self.value
		else:
			raise TypeError('index cannot be of \'NoneType\'')

	def __int__(self):
		if self.value is None and self._settings.ignore_none:
			return None
		else:
			return self._base.__int__(self.value)

	def __ipow__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self
		else:
			if self._is_of_same_base_type(other):
				self.value = self.value ** other.value
				return self._new(self.value)
			else:
				self.value = self.value ** other
				return self._new(self.value)

	def __isub__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self
		else:
			if self._is_of_same_base_type(other):
				self.value = self.value - other.value
				return self._new(self.value)
			else:
				self.value = self.value - other
				return self._new(self.value)

	def __itruediv__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self
		else:
			if self._is_of_same_base_type(other):
				self.value = self.value / other.value
				return self._new(self.value)
			else:
				self.value = self.value / other
				return self._new(self.value)

	def __le__(self, other):
		if self.value is None and self._settings.ignore_none:
			return False
		else:
			if self._is_of_same_base_type(other):
				return self.value <= other.value
			else:
				return self._base.__le__(self.value, other)

	def __lt__(self, other):
		if self.value is None and self._settings.ignore_none:
			return False
		else:
			if self._is_of_same_base_type(other):
				return self.value < other.value
			else:
				return self._base.__lt__(self.value, other)

	def __mod__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(self.value % other.value)
			else:
				return self._new(self._base.__mod__(self.value, other))

	def __mul__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(self.value * other.value)
			else:
				return self._new(self._base.__mul__(self.value, other))

	def __neg__(self):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			return self._new(self._base.__neg__(self.value))

	def __pos__(self):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			return self._new(self._base.__pos__(self.value))

	def __pow__(self, power, modulo=None):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(power):
				return self._new(pow(self.value, power.value, modulo))
			else:
				return self._new(self._base.__pow__(self.value, power))

	def __radd__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(other.value + self.value)
			else:
				return self._new(self._base.__radd__(self.value, other))

	def __rdivmod__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return divmod(other.value, self.value)
			else:
				return self._new(self._base.__rdivmod__(self.value, other))

	def __rfloordiv__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(other.value // self.value)
			else:
				return self._new(self._base.__rfloordiv__(self.value, other))

	def __rmod__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(other.value % self.value)
			else:
				return self._new(self._base.__rmod__(self.value, other))

	def __rmul__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(other.value * self.value)
			else:
				return self._new(self._base.__rmul__(self.value, other))

	def __round__(self, n=None):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			return self._new(self._base.__round__(self.value, n))

	def __rpow__(self, power, modulo=None):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(power):
				return self._new(pow(power.value, self.value, modulo))
			else:
				return self._new(self._base.__rpow__(self.value, power))

	def __rsub__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(other.value - self.value)
			else:
				return self._new(self._base.__rsub__(self.value, other))

	def __rtruediv__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(other.value / self.value)
			else:
				return self._new(self._base.__rtruediv__(self.value, other))

	def __str__(self):
		if self.value is not None:
			if self._settings.float_comma and self.header not in self._settings.dont_format:
				return '{:,}'.format(self.value)
			else:
				return str(self.value)
		else:
			return 'None'

	def __sub__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(self.value - other.value)
			else:
				return self._new(self._base.__sub__(self.value, other))

	def __truediv__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(self.value / other.value)
			else:
				return self._new(self._base.__truediv__(self.value, other))

	def __trunc__(self):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			return self._new(self._base.__trunc__(self.value))

	def as_integer_ratio(self):
		if self.value is not None:
			return self._base.as_integer_ratio(self.value)

	def conjugate(self):
		if self.value is not None:
			return self._base.conjugate(self.value)

	def hex(self):
		if self.value is not None:
			return self._base.hex(self.value)

	@property
	def imag(self):
		if self.value is not None:
			return self._base(self.value).imag

	def is_integer(self):
		if self.value is not None:
			return self._base.is_integer(self.value)

	def is_numeric(self):
		if self.value is not None:
			return True

	@property
	def real(self):
		if self.value is not None:
			return self._base(self.value).real


class DecimalCell(BaseCell):
	__slots__ = ()

	def __init__(self, value, header=None, label=None, row_num=None, col_num=None, parent=None, settings=default_settings):
		super().__init__(Decimal, value, header, label, 'decimal', row_num, col_num, parent, settings)

	def __abs__(self):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			return self._new(self._base.__abs__(self.value))

	def __add__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(self.value + other.value)
			else:
				return self._new(self._base.__add__(self.value, other))

	def __bool__(self):
		if self.value is not None:
			return self._base.__bool__(self.value)
		else:
			return False

	def __divmod__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return divmod(self.value, other.value)
			else:
				return self._new(self._base.__divmod__(self.value, other))

	def __float__(self):
		if self.value is None and self._settings.ignore_none:
			return None
		else:
			return self._base.__float__(self.value)

	def __floordiv__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(self.value // other.value)
			else:
				return self._new(self._base.__floordiv__(self.value, other))

	def __ge__(self, other):
		if self.value is None and self._settings.ignore_none:
			return False
		else:
			if self._is_of_same_base_type(other):
				return self.value >= other.value
			else:
				return self._base.__ge__(self.value, other)

	def __gt__(self, other):
		if self.value is None and self._settings.ignore_none:
			return False
		else:
			if self._is_of_same_base_type(other):
				return self.value > other.value
			else:
				return self._base.__gt__(self.value, other)

	def __iadd__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self
		else:
			if self._is_of_same_base_type(other):
				self.value = self.value + other.value
				return self._new(self.value)
			else:
				self.value = self.value + other
				return self._new(self.value)

	def __ifloordiv__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self
		else:
			if self._is_of_same_base_type(other):
				self.value = self.value // other.value
				return self._new(self.value)
			else:
				self.value = self.value // other
				return self._new(self.value)

	def __imod__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self
		else:
			if self._is_of_same_base_type(other):
				self.value = self.value % other.value
				return self._new(self.value)
			else:
				self.value = self.value % other
				return self._new(self.value)

	def __imul__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self
		else:
			if self._is_of_same_base_type(other):
				self.value = self.value * other.value
				return self._new(self.value)
			else:
				self.value = self.value * other
				return self._new(self.value)

	def __index__(self):
		if self.value is not None:
			return self.value
		else:
			raise TypeError('index cannot be of \'NoneType\'')

	def __int__(self):
		if self.value is None and self._settings.ignore_none:
			return None
		else:
			return self._base.__int__(self.value)

	def __ipow__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self
		else:
			if self._is_of_same_base_type(other):
				self.value = self.value ** other.value
				return self._new(self.value)
			else:
				self.value = self.value ** other
				return self._new(self.value)

	def __isub__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self
		else:
			if self._is_of_same_base_type(other):
				self.value = self.value - other.value
				return self._new(self.value)
			else:
				self.value = self.value - other
				return self._new(self.value)

	def __itruediv__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self
		else:
			if self._is_of_same_base_type(other):
				self.value = self.value / other.value
				return self._new(self.value)
			else:
				self.value = self.value / other
				return self._new(self.value)

	def __le__(self, other):
		if self.value is None and self._settings.ignore_none:
			return False
		else:
			if self._is_of_same_base_type(other):
				return self.value <= other.value
			else:
				return self._base.__le__(self.value, other)

	def __lt__(self, other):
		if self.value is None and self._settings.ignore_none:
			return False
		else:
			if self._is_of_same_base_type(other):
				return self.value < other.value
			else:
				return self._base.__lt__(self.value, other)

	def __mod__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(self.value % other.value)
			else:
				return self._new(self._base.__mod__(self.value, other))

	def __mul__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(self.value * other.value)
			else:
				return self._new(self._base.__mul__(self.value, other))

	def __neg__(self):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			return self._new(self._base.__neg__(self.value))

	def __pos__(self):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			return self._new(self._base.__pos__(self.value))

	def __pow__(self, power, modulo=None):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(power):
				return self._new(pow(self.value, power.value, modulo))
			else:
				return self._new(self._base.__pow__(self.value, power))

	def __radd__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(other.value + self.value)
			else:
				return self._new(self._base.__radd__(self.value, other))

	def __rdivmod__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return divmod(other.value, self.value)
			else:
				return self._new(self._base.__rdivmod__(self.value, other))

	def __rfloordiv__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(other.value // self.value)
			else:
				return self._new(self._base.__rfloordiv__(self.value, other))

	def __rmod__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(other.value % self.value)
			else:
				return self._new(self._base.__rmod__(self.value, other))

	def __rmul__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(other.value * self.value)
			else:
				r = self._new(self._base.__rmul__(self.value, other))
				if type(r) is NotImplemented:
					r = self._new(other * self.value)
				return r

	def __round__(self, n=None):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			return self._new(self._base.__round__(self.value, n))

	def __rpow__(self, power, modulo=None):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(power):
				return self._new(pow(power.value, self.value, modulo))
			else:
				return self._new(self._base.__rpow__(self.value, power))

	def __rsub__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(other.value - self.value)
			else:
				return self._new(self._base.__rsub__(self.value, other))

	def __rtruediv__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(other.value / self.value)
			else:
				return self._new(self._base.__rtruediv__(self.value, other))

	def __str__(self):
		if self.value is not None:
			if self._settings.dec_comma and self.header not in self._settings.dont_format:
				return '{:,}'.format(self.value)
			else:
				return str(self.value)
		else:
			return 'None'

	def __sub__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(self.value - other.value)
			else:
				return self._new(self._base.__sub__(self.value, other))

	def __truediv__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(self.value / other.value)
			else:
				return self._new(self._base.__truediv__(self.value, other))

	def __trunc__(self):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			return self._new(self._base.__trunc__(self.value))

	def adjusted(self):
		if self.value is not None:
			return self._base.adjusted(self.value)

	def as_tuple(self):
		if self.value is not None:
			return self._base.as_tuple(self.value)

	def canonical(self):
		if self.value is not None:
			return self

	def compare(self, other, context=None):
		if self.value is not None:
			return self._new(self._base.compare(self.value, other, context))

	def compare_signal(self, other, context=None):
		if self.value is not None:
			return self._new(self._base.compare_signal(self.value, other, context))

	def compare_total(self, other, context=None):
		if self.value is not None:
			return self._new(self._base.compare_total(self.value, other, context))

	def compare_total_mag(self, other, context=None):
		if self.value is not None:
			return self._new(self._base.compare_total_mag(self.value, other, context))

	def conjugate(self):
		if self.value is not None:
			return self

	def copy_abs(self):
		if self.value is not None:
			return self._new(self._base.copy_abs(self.value))

	def ceil(self):
		if self.value is not None:
			return self._new(self._base.ceil(self.value))

	def complex(self):
		if self.value is not None:
			return self._base.complex(self.value)

	def copy(self):
		if self.value is not None:
			return self._new(self._base.copy(self.value))

	def copy_negate(self):
		if self.value is not None:
			return self._new(self._base.copy_negate(self.value))

	def copy_sign(self, other, context=None):
		if self.value is not None:
			return self._new(self._base.copy_sign(self.value, other, context))

	def exp(self, context=None):
		if self.value is not None:
			return self._new(self._base.exp(self.value, context))

	def fma(self, other, third, context=None):
		if self.value is not None:
			return self._new(self._base.fma(self.value, other, third, context))

	@property
	def imag(self):
		if self.value is not None:
			return self._base(self.value).imag

	def is_canonical(self):
		if self.value is not None:
			return self._base.is_canonical(self.value)
		else:
			return False

	def is_finite(self):
		if self.value is not None:
			return self._base.is_finite(self.value)
		else:
			return False

	def is_infinite(self):
		if self.value is not None:
			return self._base.is_infinite(self.value)
		else:
			return False

	def is_integer(self):
		if self.value is not None:
			return self.value == int(self.value)
		else:
			return False

	def is_nan(self):
		if self.value is not None:
			return self._base.is_nan(self.value)
		else:
			return True

	def is_normal(self):
		if self.value is not None:
			return self._base.is_normal(self.value)
		else:
			return False

	def is_numeric(self):
		if self.value is not None:
			return True

	def is_qnan(self):
		if self.value is not None:
			return self._base.is_qnan(self.value)
		else:
			return True

	def is_signed(self):
		if self.value is not None:
			return self._base.is_signed(self.value)
		else:
			return False

	def is_snan(self):
		if self.value is not None:
			return self._base.is_snan(self.value)
		else:
			return True

	def is_subnormal(self):
		if self.value is not None:
			return self._base.is_subnormal(self.value)
		else:
			return False

	def is_zero(self):
		if self.value is not None:
			return self._base.is_zero(self.value)
		else:
			return False

	def ln(self):
		if self.value is not None:
			return self._new(self._base.ln(self.value))

	def log10(self):
		if self.value is not None:
			return self._new(self._base.log10(self.value))

	def logb(self):
		if self.value is not None:
			return self._new(self._base.logb(self.value))

	def logical_and(self):
		if self.value is not None:
			return self._new(self._base.logical_and(self.value))

	def logical_invert(self):
		if self.value is not None:
			return self._new(self._base.logical_invert(self.value))

	def logical_or(self):
		if self.value is not None:
			return self._new(self._base.logical_or(self.value))

	def logical_xor(self):
		if self.value is not None:
			return self._new(self._base.logical_xor(self.value))

	def max(self, other, context=None):
		if self.value is not None:
			return self._new(self._base.max(self.value, other, context))

	def max_mag(self, other, context=None):
		if self.value is not None:
			return self._new(self._base.max_mag(self.value, other, context))

	def min(self, other, context=None):
		if self.value is not None:
			return self._new(self._base.min(self.value, other, context))

	def min_mag(self, other, context=None):
		if self.value is not None:
			return self._new(self._base.min_mag(self.value, other, context))

	def next_minus(self, context=None):
		if self.value is not None:
			return self._new(self._base.next_minus(self.value, context))

	def next_plus(self, context=None):
		if self.value is not None:
			return self._new(self._base.next_plus(self.value, context))

	def next_toward(self, other, context=None):
		if self.value is not None:
			return self._new(self._base.next_toward(self.value, other, context))

	def normalize(self, context=None):
		if self.value is not None:
			return self._new(self._base.normalize(self.value, context))

	def number_class(self):
		if self.value is not None:
			return self._base.number_class(self.value)

	def quantize(self, exp, rounding=None, context=None, watchexp=True):
		if self.value is not None:
			self.value = self._base.quantize(self.value, exp, rounding, context, watchexp)
			return self

	def radix(self):
		if self.value is not None:
			return self._new(self._base.radix(self.value))

	@property
	def real(self):
		if self.value is not None:
			return self._base(self.value).real

	def remainder_near(self, other, context=None):
		if self.value is not None:
			return self._new(self._base.remainder_near(self.value, other, context))

	def rotate(self, other, context=None):
		if self.value is not None:
			return self._new(self._base.rotate(self.value, other, context))

	def same_quantum(self, other, context=None):
		if self.value is not None:
			return self._base.same_quantum(self.value, other, context)

	def scaleb(self, other, context=None):
		if self.value is not None:
			return self._new(self._base.scaleb(self.value, other, context))

	def shift(self, other, context=None):
		if self.value is not None:
			return self._new(self._base.shift(self.value, other, context))

	def sqrt(self, context=None):
		if self.value is not None:
			return self._new(self._base.sqrt(self.value, context))

	def to_eng_string(self, context=None):
		if self.value is not None:
			return self._base.to_eng_string(self.value, context)

	def to_integral(self, rounding=None, context=None):
		if self.value is not None:
			return self._base.to_integral(self.value, rounding, context)

	def to_integral_exact(self, rounding=None, context=None):
		if self.value is not None:
			return self._base.to_integral_exact(self.value, rounding, context)

	def to_integral_value(self, rounding=None, context=None):
		if self.value is not None:
			return self._base.to_integral_value(self.value, rounding, context)


class PercentCell(DecimalCell):
	__slots__ = ()

	def __init__(self, value, header=None, label=None, row_num=None, col_num=None, parent=None, settings=default_settings):
		if isinstance(value, str):
			if '%' in value:
				value = value.replace('%', '')
				value = Decimal(value) / 100
		super().__init__(value, header, label, row_num, col_num, parent, settings)
		self.column_type = 'percent'

	def __str__(self):
		if self.value is not None:
			s = str(self.value * 100)
			return '{}%'.format(locale.format('%g', Decimal(s.rstrip('0').rstrip('.')), grouping=True) if '.' in s else locale.format('%g', Decimal(s), grouping=True))
		else:
			return 'None'


class MoneyCell(DecimalCell):
	__slots__ = ()

	def __init__(self, value, header=None, label=None, row_num=None, col_num=None, parent=None, settings=default_settings):
		if isinstance(value, str):
			value = value.replace('$', '')
			value = value.replace(',', '')
		super().__init__(value, header, label, row_num, col_num, parent, settings)
		self.column_type = 'money'

	def __str__(self):
		if self.value is not None:
			if self.value < 0:
				return '-{}'.format(locale.currency(abs(float(self)), grouping=True))
			else:
				return locale.currency(float(self), grouping=True)
		else:
			return 'None'


class BooleanCell(IntCell):
	__slots__ = ()

	def __init__(self, value, header=None, label=None, row_num=None, col_num=None, parent=None, settings=default_settings):
		if isinstance(value, str):
			if value.lower() == 'false':
				value = False
		super().__init__(bool(value), header, label, row_num, col_num, parent, settings)
		self.column_type = 'bool'
		self.value = bool(value)

	def __str__(self):
		if self.value is not None:
			return str(self.value)
		else:
			return 'None'


class DateCell(BaseCell):
	__slots__ = ()

	def __init__(self, value, header=None, label=None, row_num=None, col_num=None, parent=None, settings=default_settings):
		value = parse_date_time_string(value, settings.date_format)
		super().__init__(date, value, header, label, 'date', row_num, col_num, parent, settings)

	def __add__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(self.value + other.value)
			else:
				return self._new(self._base.__add__(self.value, other))

	def __ge__(self, other):
		if self.value is None and self._settings.ignore_none:
			return False
		else:
			if self._is_of_same_base_type(other):
				return self.value >= other.value
			else:
				return self._base.__ge__(self.value, other)

	def __gt__(self, other):
		if self.value is None and self._settings.ignore_none:
			return False
		else:
			if self._is_of_same_base_type(other):
				return self.value > other.value
			else:
				return self._base.__gt__(self.value, other)

	def __iadd__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self
		else:
			if self._is_of_same_base_type(other):
				self.value = self.value + other.value
				return self._new(self.value)
			else:
				self.value = self.value + other
				return self._new(self.value)

	def __isub__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self
		else:
			if self._is_of_same_base_type(other):
				self.value = self.value - other.value
				return self._new(self.value)
			else:
				self.value = self.value - other
				return self._new(self.value)

	def __le__(self, other):
		if self.value is None and self._settings.ignore_none:
			return False
		else:
			if self._is_of_same_base_type(other):
				return self.value <= other.value
			else:
				return self._base.__le__(self.value, other)

	def __lt__(self, other):
		if self.value is None and self._settings.ignore_none:
			return False
		else:
			if self._is_of_same_base_type(other):
				return self.value < other.value
			else:
				return self._base.__lt__(self.value, other)

	def __radd__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(other.value + self.value)
			else:
				return self._new(self._base.__radd__(self.value, other))

	def __rsub__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(other.value - self.value)
			else:
				return self._new(self._base.__rsub__(self.value, other))

	def __str__(self):
		if self.value is not None:
			if 'month' in self.header.lower():
				return self.strftime('%m/%Y')
			elif 'quarter' in self.header.lower():
				return datetime_to_quarter(self.value)
			else:
				return self.strftime('%m/%d/%Y')
		else:
			return 'None'

	def __sub__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(self.value - other.value)
			else:
				r = self._base.__sub__(self.value, other)
				if r is NotImplemented:
					r = self.value - other
				return self._new(r)

	def ctime(self):
		if self.value is not None:
			return self._base.ctime(self.value)

	@property
	def day(self):
		if self.value is not None:
			return self.value.day

	def isocalendar(self):
		if self.value is not None:
			return self._base.isocalendar(self.value)

	def isoformat(self):
		if self.value is not None:
			return self._base.isoformat(self.value)

	def isoweekday(self):
		if self.value is not None:
			return self._base.isoweekday(self.value)

	def is_numeric(self):
		if self.value is not None:
			return False

	def max(self):
		if self.value is not None:
			return self._base(self.value).max

	def min(self):
		if self.value is not None:
			return self._base(self.value).min

	@property
	def month(self):
		if self.value is not None:
			return self.value.month

	def replace(self, year=None, month=None, day=None):
		if self.value is not None:
			return self._base.replace(self.value, year, month, day)

	def resolution(self):
		if self.value is not None:
			return self._base(self.value).resolution

	def strftime(self, fmt):
		if self.value is not None:
			return self._base.strftime(self.value, fmt)

	def timetuple(self):
		if self.value is not None:
			return self._base.timetuple(self.value)

	def toordinal(self):
		if self.value is not None:
			return self._base.toordinal(self.value)

	def weekday(self):
		if self.value is not None:
			return self._base.weekday(self.value)

	@property
	def year(self):
		if self.value is not None:
			return self.value.year


class TimeCell(BaseCell):
	__slots__ = ()

	def __init__(self, value, header=None, label=None, row_num=None, col_num=None, parent=None, settings=default_settings):
		value = parse_date_time_string(value, settings.time_format)
		super().__init__(time, value, header, label, 'time', row_num, col_num, parent, settings)

	def __bool__(self):
		if self.value is not None:
			return self._base.__bool__(self.value)
		else:
			return False

	def __ge__(self, other):
		if self.value is None and self._settings.ignore_none:
			return False
		else:
			if self._is_of_same_base_type(other):
				return self.value >= other.value
			else:
				return self._base.__ge__(self.value, other)

	def __gt__(self, other):
		if self.value is None and self._settings.ignore_none:
			return False
		else:
			if self._is_of_same_base_type(other):
				return self.value > other.value
			else:
				return self._base.__gt__(self.value, other)

	def __le__(self, other):
		if self.value is None and self._settings.ignore_none:
			return False
		else:
			if self._is_of_same_base_type(other):
				return self.value <= other.value
			else:
				return self._base.__le__(self.value, other)

	def __lt__(self, other):
		if self.value is None and self._settings.ignore_none:
			return False
		else:
			if self._is_of_same_base_type(other):
				return self.value < other.value
			else:
				return self._base.__lt__(self.value, other)

	def dst(self):
		if self.value is not None:
			return self._base.dst(self.value)

	@property
	def hour(self):
		if self.value is not None:
			return self.value.hour

	def isoformat(self):
		if self.value is not None:
			return self._base.isoformat(self.value)

	def is_numeric(self):
		if self.value is not None:
			return False

	def max(self):
		if self.value is not None:
			return self._base(self.value).max

	@property
	def microsecond(self):
		if self.value is not None:
			return self.value.microsecond

	def min(self):
		if self.value is not None:
			return self._base(self.value).min

	@property
	def minute(self):
		if self.value is not None:
			return self.value.minute

	def replace(self, hour=None, minute=None, second=None, microsecond=None, tzinfo=True):
		if self.value is not None:
			return self._new(self._base.replace(self.value, hour, minute, second, microsecond, tzinfo))

	def resolution(self):
		if self.value is not None:
			return self._base(self.value).resolution

	@property
	def second(self):
		if self.value is not None:
			return self.value.second

	def strftime(self, fmt):
		if self.value is not None:
			return self._base.strftime(self.value, fmt)

	@property
	def tzinfo(self):
		if self.value is not None:
			return self.value.tzinfo

	def tzname(self):
		if self.value is not None:
			return self._base.tzname(self.value)

	def utcoffset(self):
		if self.value is not None:
			return self._base.utcoffset(self.value)


class SecondsCell(IntCell):
	__slots__ = ()

	def __init__(self, value, header=None, label=None, row_num=None, col_num=None, parent=None, settings=default_settings):
		if isinstance(value, datetime):
			value = seconds_since_epoch(value)
		elif isinstance(value, str):
			value = seconds_since_epoch(datetime.strptime(value, '%Y/%m/%d'))
		super().__init__(value, header, label, row_num, col_num, parent, settings)
		self.column_type = 'seconds'


class TimestampCell(BaseCell):
	__slots__ = ()

	def __init__(self, value, header=None, label=None, row_num=None, col_num=None, parent=None, settings=default_settings):
		value = parse_date_time_string(value, settings.datetime_format)
		super().__init__(datetime, value, header, label, 'timestamp', row_num, col_num, parent, settings)

	def __add__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(self.value + other.value)
			else:
				return self._new(self._base.__add__(self.value, other))

	def __ge__(self, other):
		if self.value is None and self._settings.ignore_none:
			return False
		else:
			if self._is_of_same_base_type(other):
				return self.value >= other.value
			else:
				return self._base.__ge__(self.value, other)

	def __gt__(self, other):
		if self.value is None and self._settings.ignore_none:
			return False
		else:
			if self._is_of_same_base_type(other):
				return self.value > other.value
			else:
				return self._base.__gt__(self.value, other)

	def __iadd__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self
		else:
			if self._is_of_same_base_type(other):
				self.value = self.value + other.value
				return self._new(self.value)
			else:
				self.value = self.value + other
				return self._new(self.value)

	def __isub__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self
		else:
			if self._is_of_same_base_type(other):
				self.value = self.value - other.value
				return self._new(self.value)
			else:
				self.value = self.value - other
				return self._new(self.value)

	def __le__(self, other):
		if self.value is None and self._settings.ignore_none:
			return False
		else:
			if self._is_of_same_base_type(other):
				return self.value <= other.value
			else:
				return self._base.__le__(self.value, other)

	def __lt__(self, other):
		if self.value is None and self._settings.ignore_none:
			return False
		else:
			if self._is_of_same_base_type(other):
				return self.value < other.value
			else:
				return self._base.__lt__(self.value, other)

	def __radd__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(other.value + self.value)
			else:
				return self._new(self._base.__radd__(self.value, other))

	def __rsub__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(other.value - self.value)
			else:
				return self._new(self._base.__rsub__(self.value, other))

	def __str__(self):
		if self.value is not None:
			return self.strftime(self._settings.datetime_format)
		else:
			return 'None'

	def __sub__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(self.value - other.value)
			else:
				r = self._base.__sub__(self.value, other)
				if r is NotImplemented:
					r = self.value - other
				return self._new(r)

	def astimezone(self, tz=None):
		if self.value is not None:
			return self._new(self._base.astimezone(self.value, tz))

	def ctime(self):
		if self.value is not None:
			return self._base.ctime(self.value)

	def date(self):
		if self.value is not None:
			return DateCell(self._base.date(self.value), self.header, self.label, self.row_num, self.col_num, self._parent)

	@property
	def day(self):
		if self.value is not None:
			return self.value.day

	def dst(self):
		if self.value is not None:
			return self._base.dst(self.value)

	@property
	def hour(self):
		if self.value is not None:
			return self.value.hour

	def isocalendar(self):
		if self.value is not None:
			return self._base.isocalendar(self.value)

	def isoformat(self, sep='T'):
		if self.value is not None:
			return self._base.isoformat(self.value, sep)

	def isoweekday(self):
		if self.value is not None:
			return self._base.isoweekday(self.value)

	def is_numeric(self):
		if self.value is not None:
			return False

	def max(self):
		if self.value is not None:
			return self._base(self.value).max

	@property
	def microsecond(self):
		if self.value is not None:
			return self.value.microsecond

	def min(self):
		if self.value is not None:
			return self._base(self.value).min

	@property
	def minute(self):
		if self.value is not None:
			return self.value.minute

	@property
	def month(self):
		if self.value is not None:
			return self.value.month

	def replace(self, year=None, month=None, day=None, hour=None, minute=None, second=None, microsecond=None, tzinfo=True):
		if self.value is not None:
			return self._new(self._base.replace(self.value, year, month, day, hour, minute, second, microsecond, tzinfo))

	def resolution(self):
		if self.value is not None:
			return self._base(self.value).resolution

	@property
	def second(self):
		if self.value is not None:
			return self.value.second

	def strftime(self, fmt):
		if self.value is not None:
			return self._base.strftime(self.value, fmt)

	def time(self):
		if self.value is not None:
			return TimeCell(self._base.time(self.value), self.header, self.label, self.row_num, self.col_num, self._parent)

	def timestamp(self):
		if self.value is not None:
			return self._base.timestamp(self.value)

	def timetuple(self):
		if self.value is not None:
			return self._base.timetuple(self.value)

	def timetz(self):
		if self.value is not None:
			return TimeCell(self._base.timetz(self.value), self.header, self.label, self.row_num, self.col_num, self._parent)

	def toordinal(self):
		if self.value is not None:
			return self._base.toordinal(self.value)

	@property
	def tzinfo(self):
		if self.value is not None:
			return self.value.tzinfo

	def tzname(self):
		if self.value is not None:
			return self._base.tzname(self.value)

	def utcoffset(self):
		if self.value is not None:
			return IntervalCell(self._base.utcoffset(self.value), self.header, self.label, self.row_num, self.col_num, self._parent)

	def utctimetuple(self):
		if self.value is not None:
			return self._base.utctimetuple(self.value)

	def weekday(self):
		if self.value is not None:
			return self._base.weekday(self.value)

	@property
	def year(self):
		if self.value is not None:
			return self.value.year


class IntervalCell(BaseCell):
	__slots__ = ()

	def __init__(self, value, header=None, label=None, row_num=None, col_num=None, parent=None, settings=default_settings):
		if isinstance(value, str):
			value = parse_time_delta(value)
		super().__init__(timedelta, value, header, label, 'interval', row_num, col_num, parent, settings)

	def __abs__(self):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			return self._new(self._base.__abs__(self.value))

	def __add__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(self.value + other.value)
			else:
				return self._new(self._base.__add__(self.value, other))

	def __bool__(self):
		if self.value is not None:
			return self._base.__bool__(self.value)
		else:
			return False

	def __divmod__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return divmod(self.value, other.value)
			else:
				return self._new(self._base.__divmod__(self.value, other))

	def __floordiv__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(self.value // other.value)
			else:
				return self._new(self._base.__floordiv__(self.value, other))

	def __ge__(self, other):
		if self.value is None and self._settings.ignore_none:
			return False
		else:
			if self._is_of_same_base_type(other):
				return self.value >= other.value
			else:
				return self._base.__ge__(self.value, other)

	def __gt__(self, other):
		if self.value is None and self._settings.ignore_none:
			return False
		else:
			if self._is_of_same_base_type(other):
				return self.value > other.value
			else:
				return self._base.__gt__(self.value, other)

	def __iadd__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self
		else:
			if self._is_of_same_base_type(other):
				self.value = self.value + other.value
				return self._new(self.value)
			else:
				self.value = self.value + other
				return self._new(self.value)

	def __ifloordiv__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self
		else:
			if self._is_of_same_base_type(other):
				self.value = self.value // other.value
				return self._new(self.value)
			else:
				self.value = self.value // other
				return self._new(self.value)

	def __imod__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self
		else:
			if self._is_of_same_base_type(other):
				self.value = self.value % other.value
				return self._new(self.value)
			else:
				self.value = self.value % other
				return self._new(self.value)

	def __imul__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self
		else:
			if self._is_of_same_base_type(other):
				self.value = self.value * other.value
				return self._new(self.value)
			else:
				self.value = self.value * other
				return self._new(self.value)

	def __isub__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self
		else:
			if self._is_of_same_base_type(other):
				self.value = self.value - other.value
				return self._new(self.value)
			else:
				self.value = self.value - other
				return self._new(self.value)

	def __itruediv__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self
		else:
			if self._is_of_same_base_type(other):
				self.value = self.value / other.value
				return self._new(self.value)
			else:
				self.value = self.value / other
				return self._new(self.value)

	def __le__(self, other):
		if self.value is None and self._settings.ignore_none:
			return False
		else:
			if self._is_of_same_base_type(other):
				return self.value <= other.value
			else:
				return self._base.__le__(self.value, other)

	def __lt__(self, other):
		if self.value is None and self._settings.ignore_none:
			return False
		else:
			if self._is_of_same_base_type(other):
				return self.value < other.value
			else:
				return self._base.__lt__(self.value, other)

	def __mod__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(self.value % other.value)
			else:
				return self._new(self._base.__mod__(self.value, other))

	def __mul__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(self.value * other.value)
			else:
				return self._new(self._base.__mul__(self.value, other))

	def __neg__(self):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			return self._new(self._base.__neg__(self.value))

	def __pos__(self):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			return self._new(self._base.__pos__(self.value))

	def __radd__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(other.value + self.value)
			else:
				return self._new(self._base.__radd__(self.value, other))

	def __rdivmod__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return divmod(other.value, self.value)
			else:
				return self._new(self._base.__rdivmod__(self.value, other))

	def __rfloordiv__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(other.value // self.value)
			else:
				return self._new(self._base.__rfloordiv__(self.value, other))

	def __rmod__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(other.value % self.value)
			else:
				return self._new(self._base.__rmod__(self.value, other))

	def __rmul__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(other.value * self.value)
			else:
				return self._new(self._base.__rmul__(self.value, other))

	def __rsub__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(other.value - self.value)
			else:
				return self._new(self._base.__rsub__(self.value, other))

	def __rtruediv__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(other.value / self.value)
			else:
				return self._new(self._base.__rtruediv__(self.value, other))

	def __sub__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(self.value - other.value)
			else:
				return self._new(self._base.__sub__(self.value, other))

	def __truediv__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(self.value / other.value)
			else:
				return self._new(self._base.__truediv__(self.value, other))

	@property
	def days(self):
		if self.value is not None:
			return self.value.days

	def is_numeric(self):
		if self.value is not None:
			return False

	def max(self):
		if self.value is not None:
			return self._base(self.value).max

	@property
	def microseconds(self):
		if self.value is not None:
			return self.value.microseconds

	def min(self):
		if self.value is not None:
			return self._base(self.value).min

	def resolution(self):
		if self.value is not None:
			return self._base(self.value).resolution

	@property
	def seconds(self):
		if self.value is not None:
			return self.value.seconds

	def total_seconds(self):
		if self.value is not None:
			return self._base.total_seconds(self.value)


class ListCell(BaseCell):
	__slots__ = ()

	def __init__(self, value, header=None, label=None, row_num=None, col_num=None, parent=None, settings=default_settings):
		super().__init__(list, value, header, label, 'list', row_num, col_num, parent, settings)

	def __add__(self, other):
		if self.value is None and self._settings.ignore_none:
			return self._new(self.value)
		else:
			if self._is_of_same_base_type(other):
				return self._new(self.value + other.value)
			else:
				return self._new(self._base.__add__(self.value, other))

	def __contains__(self, item):
		pass

	def is_numeric(self):
		if self.value is not None:
			return False

try:
	# noinspection PyUnresolvedReferences
	from psycopg2.extensions import register_adapter

	def adapt_string_cell(str_cell):
		str_cell.getquoted = lambda: "'{}'".format(str_cell.value)
		return str_cell

	register_adapter(StrCell, adapt_string_cell)

	def adapt_int_cell(int_cell):
		int_cell.getquoted = lambda: "'{}'".format(int_cell.value)
		return int_cell

	register_adapter(IntCell, adapt_int_cell)

	def adapt_float_cell(float_cell):
		float_cell.getquoted = lambda: "'{}'".format(float_cell.value)
		return float_cell

	register_adapter(FloatCell, adapt_float_cell)

	def adapt_decimal_cell(decimal_cell):
		decimal_cell.getquoted = lambda: "'{}'".format(decimal_cell.value)
		return decimal_cell

	register_adapter(DecimalCell, adapt_decimal_cell)

	def adapt_percent_cell(percent_cell):
		percent_cell.getquoted = lambda: "'{}'".format(percent_cell.value)
		return percent_cell

	register_adapter(PercentCell, adapt_percent_cell)

	def adapt_money_cell(money_cell):
		money_cell.getquoted = lambda: "'{}'".format(money_cell.value)
		return money_cell

	register_adapter(MoneyCell, adapt_money_cell)

	def adapt_boolean_cell(bool_cell):
		bool_cell.getquoted = lambda: "'{}'".format(bool_cell.value)
		return bool_cell

	register_adapter(BooleanCell, adapt_boolean_cell)

	def adapt_date_cell(date_cell):
		date_cell.getquoted = lambda: "'{}'".format(date_cell.value)
		return date_cell

	register_adapter(DateCell, adapt_date_cell)

	def adapt_time_cell(time_cell):
		time_cell.getquoted = lambda: "'{}'".format(time_cell.value)
		return time_cell

	register_adapter(TimeCell, adapt_time_cell)

	def adapt_seconds_cell(seconds_cell):
		seconds_cell.getquoted = lambda: "'{}'".format(seconds_cell.value)
		return seconds_cell

	register_adapter(SecondsCell, adapt_seconds_cell)

	def adapt_timestamp_cell(timestamp_cell):
		timestamp_cell.getquoted = lambda: "'{}'".format(timestamp_cell.value)
		return timestamp_cell

	register_adapter(TimestampCell, adapt_timestamp_cell)

	def adapt_interval_cell(interval_cell):
		interval_cell.getquoted = lambda: "'{}'".format(interval_cell.value)
		return interval_cell

	register_adapter(IntervalCell, adapt_interval_cell)
except ImportError:
	pass
