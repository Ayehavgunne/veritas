from tabularpy import cells

operators = ('=', '!=', '<', '>', '<=', '>=', 'IS', 'IN')


class Operator(object):
	def __init__(self, operator):
		self.operator = operator

	def __str__(self):
		return self.operator


class Is(Operator):
	def __init__(self):
		super().__init__('IS')


class In(Operator):
	def __init__(self, iterable):
		super().__init__('IN')
		self.iterable = iterable

	def __str__(self):
		values = ''
		for value in self.iterable:
			if isinstance(value, (list, set, tuple)):
				if len(value) > 1:
					values = '{}('.format(values)
					for val in value:
						if isinstance(val, (cells.StrCell, cells.DateCell, cells.TimeCell, cells.TimestampCell)):
							values = "{}'{}', ".format(values, val)
						else:
							values = '{}{}, '.format(values, val)
					values = '{}), '.format(values[:-2])
				else:
					if isinstance(value[0], (cells.StrCell, cells.DateCell, cells.TimeCell, cells.TimestampCell)):
						values = "{}'{}', ".format(values, value[0])
					else:
						values = '{}{}, '.format(values, value[0])
			else:
				if isinstance(value, (cells.StrCell, cells.DateCell, cells.TimeCell, cells.TimestampCell)):
					values = "{}'{}', ".format(values, value)
				else:
					values = '{}{}, '.format(values, value)
		values = '{}'.format(values[:-2])
		return 'IN ({})'.format(values)


class Equals(Operator):
	def __init__(self):
		super().__init__('=')


class NotEquals(Operator):
	def __init__(self):
		super().__init__('!=')


class LessThan(Operator):
	def __init__(self):
		super().__init__('<')


class GreaterThan(Operator):
	def __init__(self):
		super().__init__('>')


class LessThanEquals(Operator):
	def __init__(self):
		super().__init__('<=')


class GreaterThanEquals(Operator):
	def __init__(self):
		super().__init__('>=')
