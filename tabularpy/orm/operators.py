from . import column as col


class Operator(object):
	def __init__(self, operator, quoted):
		self.operator = operator
		self.quoted = quoted

	def __str__(self):
		return self.operator

	def __repr__(self):
		return "{}('{}')".format(type(self).__name__, self.operator)


class ArithmeticOperator(Operator):
	def __init__(self, operator, operand, quoted):
		super().__init__(operator, quoted)
		self.operand = operand

	def __str__(self):
		if self.quoted:
			return "{} '{}'".format(self.operator, self.operand)
		else:
			return "{} {}".format(self.operator, self.operand)


class Add(ArithmeticOperator):
	def __init__(self, operand, quoted=False):
		super().__init__('+', operand, quoted=quoted)


class Subtract(ArithmeticOperator):
	def __init__(self, operand, quoted=False):
		super().__init__('-', operand, quoted=quoted)


class Multiply(ArithmeticOperator):
	def __init__(self, operand, quoted=False):
		super().__init__('*', operand, quoted=quoted)


class Divide(ArithmeticOperator):
	def __init__(self, operand, quoted=False):
		super().__init__('/', operand, quoted=quoted)


class Mod(ArithmeticOperator):
	def __init__(self, operand, quoted=False):
		super().__init__('%', operand, quoted=quoted)


class ComparisonOperator(Operator):
	def __init__(self, operator, operand, quoted):
		super().__init__(operator, quoted)
		self.operand = operand

	def __str__(self):
		if self.quoted:
			return "{} '{}'".format(self.operator, self.operand)
		else:
			return '{} {}'.format(self.operator, self.operand)


class Equals(ComparisonOperator):
	def __init__(self, operand, quoted=False):
		super().__init__('=', operand, quoted)


class NotEquals(ComparisonOperator):
	def __init__(self, operand, quoted=False):
		super().__init__('!=', operand, quoted)


class LessThan(ComparisonOperator):
	def __init__(self, operand, quoted=False):
		super().__init__('<', operand, quoted)


class GreaterThan(ComparisonOperator):
	def __init__(self, operand, quoted=False):
		super().__init__('>', operand, quoted)


class LessThanEquals(ComparisonOperator):
	def __init__(self, operand, quoted=False):
		super().__init__('<=', operand, quoted)


class GreaterThanEquals(ComparisonOperator):
	def __init__(self, operand, quoted=False):
		super().__init__('>=', operand, quoted)


class LogicalOperator(Operator):
	def __init__(self, operator, *operands, quoted=False):
		super().__init__(operator, quoted)
		self.operands = operands

	def __str__(self):
		if self.quoted:
			return "{} '{}'".format(self.operator, self.operands[0])
		else:
			return '{} {}'.format(self.operator, self.operands[0])


class And(LogicalOperator):
	def __init__(self, *operands, quoted=False):
		super().__init__('AND', *operands, quoted=quoted)

	def __str__(self):
		sql = '('
		for x, operand in enumerate(self.operands):
			if x == 0:
				sql = '{}{}'.format(sql, operand)
			else:
				sql = '{} {} {}'.format(sql, self.operator, operand)
		return '{})'.format(sql)


class Or(LogicalOperator):
	def __init__(self, *operands, quoted=False):
		super().__init__('OR', *operands, quoted=quoted)

	def __str__(self):
		sql = '('
		for x, operand in enumerate(self.operands):
			if x == 0:
				sql = '{}{}'.format(sql, operand)
			else:
				sql = '{} {} {}'.format(sql, self.operator, operand)
		return '{})'.format(sql)


class Is(LogicalOperator):
	def __init__(self, operand, quoted=False):
		super().__init__('IS', operand, quoted=quoted)


class Not(LogicalOperator):
	def __init__(self, operand, quoted=False):
		super().__init__('NOT', operand, quoted=quoted)


class In(LogicalOperator):
	def __init__(self, iterable, quoted=False):
		super().__init__('IN', iterable, quoted=quoted)

	def __str__(self):
		values = ''
		for value in self.operands:
			if isinstance(value, (list, set, tuple)):
				if len(value) > 1:
					values = '{}('.format(values)
					for val in value:
						if self.quoted:
							values = "{}'{}', ".format(values, val)
						elif isinstance(val, col.Column):
							values = "{}%({})s, ".format(values, val.name)
						else:
							values = '{}{}, '.format(values, val)
					values = '{}), '.format(values[:-2])
				else:
					if self.quoted:
						values = "{}'{}', ".format(values, value[0])
					elif isinstance(value[0], col.Column):
						values = "{}%({})s, ".format(values, value[0].name)
					else:
						values = '{}{}, '.format(values, value[0])
			else:
				if self.quoted:
					values = "{}'{}', ".format(values, value)
				elif isinstance(value, col.Column):
					values = "{}%({})s, ".format(values, value.name)
				else:
					values = '{}{}, '.format(values, value)
		values = '{}'.format(values[:-2])
		if isinstance(self.operands[0], col.Column):
			return '{} ({})'.format(self.operator, values)
		return '{} {}'.format(self.operator, values)


class Between(LogicalOperator):
	def __init__(self, first_operand, second_operand, quoted=False):
		super().__init__(first_operand, second_operand, quoted=quoted)

	def __str__(self):
		return '{} {} AND {}'.format(self.operator, self.operands[0], self.operands[1])


class Like(LogicalOperator):
	def __init__(self, operand, quoted=False):
		super().__init__('LIKE', operand, quoted=quoted)


class All(LogicalOperator):
	pass


class Any(LogicalOperator):
	pass


class Exists(LogicalOperator):
	pass


class Unique(LogicalOperator):
	pass


class Modifyer(Operator):
	def __init__(self, operator):
		super().__init__(operator, False)


class As(Modifyer):
	def __init__(self, column, label):
		super().__init__('AS')
		self.column = column
		self.label = label

	def __str__(self):
		return '{} {} {}'.format(self.column.name, self.operator, self.label)


class Desc(Modifyer):
	def __init__(self, column):
		super().__init__('DESC')
		self.column = column

	def __str__(self):
		return '{} {}'.format(self.column.name, self.operator)
