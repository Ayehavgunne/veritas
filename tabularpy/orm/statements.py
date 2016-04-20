from tabularpy.orm.conditions import Condition
from . import database
from . import table as tbl
from .operators import In
from .operators import Desc
from .column import Column


class Statement(object):
	def __init__(self, table, on=None):
		self.sql = ''
		self.table = table
		self.on = on
		self.table_name = table.name

	def compose(self, *conditions):
		for x, condition in enumerate(conditions):
			if isinstance(condition, Column):
				if x == 0:
					self.sql = '{0} WHERE {1} = %({1})s'.format(self.sql, condition.name)
				else:
					self.sql = '{0} AND {1} = %({1})s'.format(self.sql, condition.name)
			else:
				if x == 0:
					self.sql = '{} WHERE {}'.format(self.sql, condition)
				else:
					self.sql = '{} AND {}'.format(self.sql, condition)

	def execute(self, cursor=None):
		if cursor:
			self._execute(cursor)
			results = cursor.fetchall()
		else:
			with self.table.parent.cursor_manager() as cursor:
				self._execute(cursor)
				results = cursor.results
		return results

	def _execute(self, cursor):
		if self.table.data:
			if self.on:
				cursor.executemany(self.sql, self.table.data.to_list_of_dicts(*self.on))
			else:
				cursor.executemany(self.sql, self.table.data.to_list_of_dicts())
		else:
			cursor.execute(self.sql)

	def __str__(self):
		return self.sql


class Create(Statement):
	def __init__(self, obj):
		super().__init__(obj)
		if isinstance(obj, tbl.Table):
			self.sql = 'CREATE TABLE {} '.format(obj.name)
			columns = '('
			for column in obj.columns:
				columns = '{}{}, '.format(columns, column)
			if obj.primary_keys:
				columns = '{}CONSTRAINT {}_pkey PRIMARY KEY ('.format(columns, obj.name)
				for column in obj.primary_keys:
					columns = '{}{}, '.format(columns, column)
				columns = '{}), '.format(columns[:-2])
			if obj.uniques:
				for unq in obj.uniques:
					columns = '{0}CONSTRAINT {1}_{2}_key UNIQUE ({2}), '.format(columns, obj.name, unq)
			self.sql = '{}{});'.format(self.sql, columns[:-2])
			if obj.indexes:
				for idx in obj.indexes:
					self.sql = '{0} CREATE INDEX {1}_{2}_idx ON {1} USING btree ({2});'.format(self.sql, obj.name, idx)
		elif isinstance(obj, database.Database):
			self.sql = 'CREATE DATABASE {};'.format(obj.name)


class CreateTemp(Statement):
	def __init__(self, table, original_name):
		super().__init__(table)
		self.sql = 'CREATE TABLE {} AS SELECT * FROM {} LIMIT 0;'.format(table.name, original_name)


class TableCopy(Statement):
	def __init__(self, from_table, to_table, *columns):
		super().__init__(from_table)
		self.sql = 'INSERT INTO {}'.format(to_table.name)
		selects = ''
		if columns:
			self.sql = '{}('.format(self.sql)
			for column in columns:
				self.sql = '{}{}, '.format(self.sql, column.name)
				selects = '{}{}, '.format(selects, column.name)
			self.sql = '{}) SELECT {} FROM {}'.format(self.sql[:-2], selects[:-2], self.table.name)
		else:
			self.sql = '{}{} SELECT * FROM {}'.format(self.sql, to_table.name, self.table.name)


class Select(Statement):
	def __init__(self, table, *columns):
		super().__init__(table)
		self.sql = 'SELECT'
		if not columns:
			self.sql = '{} *, '.format(self.sql)
		for column in columns:
			if isinstance(column, Condition):
				self.sql = '{} {}, '.format(self.sql, column)
			else:
				self.sql = '{}{}, '.format(self.sql, column.name)
		self.sql = '{} FROM {}'.format(self.sql[:-2], self.table.name)

	def where(self, *conditions):
		return Where(self.table, self.sql, *conditions)

	def order_by(self, *columns):
		return OrderBy(self.table, self.sql, *columns)

	def limit(self, num_rows):
		return Limit(self.table, self.sql, num_rows)


class Insert(Statement):
	def __init__(self, table):
		super().__init__(table)
		self.sql = 'INSERT INTO {}'.format(self.table.name)
		columns = '('
		values = '('
		for column in self.table.columns:
			# noinspection PyProtectedMember
			if not column._ignore and not column.serial:
				columns = '{}{}, '.format(columns, column.name)
				values = '{}%({})s, '.format(values, column.name)
		self.sql = '{} {}) VALUES {});'.format(self.sql, columns[:-2], values[:-2])


class CopyFromFile(Statement):
	def __init__(self, table, absolute_path):
		super().__init__(table)
		self.sql = "COPY {} FROM '{}'".format(self.table.name, absolute_path)
		if absolute_path.split('.')[-1].lower() == 'csv':
			self.sql = '{} CSV'.format(self.sql)
		self.sql = '{};'.format(self.sql)


class Update(Statement):
	def __init__(self, table):
		super().__init__(table)
		self.sql = 'UPDATE {} SET '.format(self.table.name)
		values = ''
		for column in self.table.columns:
			# noinspection PyProtectedMember
			if not column._ignore:
				values = '{0}{1} = %({1})s, '.format(values, column.name)
		self.sql = '{}{}'.format(self.sql, values[:-2])

	def where(self, *conditions):
		return Where(self.table, self.sql, *conditions)


class Delete(Statement):
	def __init__(self, table, *on):
		super().__init__(table, on)
		self.sql = 'DELETE FROM {}'.format(self.table.name)

	def where(self, *conditions):
		return Where(self.table, self.sql, *conditions)


class InnerJoin(Statement):
	def __init__(self, table1, table2, *conditions):
		super().__init__(table1)
		self.sql = 'INNER JOIN {} ON'.format(table2.name)


class Drop(Statement):
	def __init__(self, table, cascaded=False):
		super().__init__(table)
		self.sql = 'DROP TABLE {}'.format(self.table.name)
		if cascaded:
			self.sql = '{} CASCADED'.format(self.sql)
		self.sql = '{};'.format(self.sql)


class Where(Statement):
	def __init__(self, table, sql, *conditions):
		super().__init__(table)
		self.sql = sql
		self.compose(*conditions)

	def order_by(self, *columns):
		return OrderBy(self.table, self.sql, *columns)

	def limit(self, num_rows):
		return Limit(self.table, self.sql, num_rows)


class OrderBy(Statement):
	def __init__(self, table, sql, *columns):
		super().__init__(table)
		self.sql = '{} ORDER BY'.format(sql)
		for column in columns:
			if isinstance(column, Desc):
				self.sql = '{} {}, '.format(self.sql, column)
			else:
				self.sql = '{} {}, '.format(self.sql, column.name)
		self.sql = '{}'.format(self.sql[:-2])

	def limit(self, num_rows):
		return Limit(self.table, self.sql, num_rows)


class Limit(Statement):
	def __init__(self, table, sql, num_rows):
		super().__init__(table)
		self.sql = '{} LIMIT {};'.format(sql, num_rows)


class Tuple(Statement):
	def __init__(self, table, *columns):
		super().__init__(table)
		self.sql = '({})'.format(', '.join(column.name for column in columns))

	def in_(self, iterable):
		return '{} {}'.format(self.sql, In(iterable))

	def limit(self, num_rows):
		return Limit(self.table, self.sql, num_rows)


class BlankStatement(Statement):
	def __init__(self, table):
		super().__init__(table)

	def execute(self, cursor=None):
		pass
