class Condition(object):
	def __init__(self, left_operand, operator):
		self.left_operand = left_operand
		self.operator = operator

	def __str__(self):
		return '{} {}'.format(self.left_operand.name, self.operator)
