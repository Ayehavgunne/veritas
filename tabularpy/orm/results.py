from .column import Column
from ..row import Row
from .. import tables


# TODO: Enhance this class to provide the results in a more robust way
class Results(object):
	def __init__(self, cursor, database):
		self.cursor = cursor
		self.database = database
		self._i = 0
		self.buffer = []
		self.columns = []

	def __iter__(self):
		return self

	def __next__(self):
		if self._i < len(self.buffer):
			row = self.buffer[self._i]
			row = Row(
				list(row),
				self.get_column_names(),
				self.get_column_types(),
				self._i,
				self
			)
			self._i += 1
			return row
		else:
			self._i = 0
			self.buffer = []
			raise StopIteration

	def fill_buffer(self, data):
		self.buffer.extend(data)
		self.fill_columns()
		pass

	# I can feel the columns in the air tonight!    Hold on!
	def fill_columns(self):
		for column in self.cursor.description:
			if not self.has_column(column.name):
				self.columns.append(Column(column[0], column[1], self, self.database))

	def get_column_names(self):
		return [column.name for column in self.columns]

	def get_column_types(self):
		return {column.name: column.type_ for column in self.columns}

	def to_data_table(self):
		table = tables.ResultsTable(self.get_column_names(), column_types=self.get_column_types(), name='ResultsTable')
		for row in self:
			table.add_row(row)
		return table

	def has_column(self, name):
		for column in self.columns:
			if column.name == name:
				return True
		return False

	def change_cell(self, *args, **kwargs):
		pass
