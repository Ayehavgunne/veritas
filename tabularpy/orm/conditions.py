from .types import Varchar
from .types import Date
from .types import Time
from .types import Timestamp
from .operators import operators
from .operators import Equals
from .operators import NotEquals
from .operators import LessThan
from .operators import GreaterThan
from .operators import LessThanEquals
from .operators import GreaterThanEquals
from .operators import Operator
from .operators import Is


class Condition(object):
	def __init__(self, condition, *columns):
		self.tokens = condition.split(' ')
		for x, token in enumerate(self.tokens):
			for column in columns:
				if token == column.name:
					self.tokens[x] = ColRef(column)
				elif token == '*':
					self.tokens[x] = Wildcard()
				elif token in operators:
					if token == 'IS':
						self.tokens[x] = Is()
					elif token == '=':
						self.tokens[x] = Equals()
					elif token == '!=':
						self.tokens[x] = NotEquals()
					elif token == '<':
						self.tokens[x] = LessThan()
					elif token == '>':
						self.tokens[x] = GreaterThan()
					elif token == '<=':
						self.tokens[x] = LessThanEquals()
					elif token == '>=':
						self.tokens[x] = GreaterThanEquals()
					else:
						self.tokens[x] = Operator(token)
				else:
					self.tokens[x] = Operand(token, column.type_)
		for x in reversed(range(len(self.tokens))):
			if x != 0:
				self.tokens.insert(x, Whitespace())

	def __str__(self):
		return ''.join([str(token) for token in self.tokens])

class ConditionLogic(object):
	def __init__(self, *conditions):
		self.conditions = conditions


class And(ConditionLogic):
	def __init__(self, *conditions):
		super().__init__(*conditions)

	def __str__(self):
		sql = '('
		for x, condition in enumerate(self.conditions):
			if x == 0:
				sql = '{}{}'.format(sql, condition)
			else:
				sql = '{} AND {}'.format(sql, condition)
		return '{})'.format(sql)


class Or(ConditionLogic):
	def __init__(self, *conditions):
		super().__init__(*conditions)

	def __str__(self):
		sql = '('
		for x, condition in enumerate(self.conditions):
			if x == 0:
				sql = '{}{}'.format(sql, condition)
			else:
				sql = '{} OR {}'.format(sql, condition)
		return '{})'.format(sql)


class Not(ConditionLogic):
	def __init__(self, condition):
		super().__init__(condition)

	def __str__(self):
		return 'NOT {}'.format(self.conditions[0])


class ColRef(object):
	def __init__(self, column):
		self.column = column

	def __str__(self):
		return self.column.name


class Operand(object):
	def __init__(self, operand, type_):
		self.operand = operand.replace("'", '')
		self.type_ = type_

	def __str__(self):
		if isinstance(self.type_, (Varchar, Date, Time, Timestamp)):
			return "'{}'".format(self.operand)
		else:
			return self.operand


class Whitespace(object):
	def __str__(self):
		return ' '


class Wildcard(object):
	def __str__(self):
		return '*'