from tabularpy.orm import database
from tabularpy.orm import table as tbl
from tabularpy.orm.operators import In
from .column import Column
from .conditions import Condition


class Statement(object):
	def __init__(self, table):
		self.sql = ''
		self.table = table

	def compose(self, *conditions):
		for x, condition in enumerate(conditions):
			if isinstance(condition, Column):
				if x == 0:
					self.sql = '{0} WHERE {1} = %({1})s'.format(self.sql, condition.name)
				else:
					self.sql = '{0} AND {1} = %({1})s'.format(self.sql, condition.name)
			elif isinstance(condition, Condition):
				if x == 0:
					self.sql = '{} WHERE {}'.format(self.sql, condition)
				else:
					self.sql = '{} AND {}'.format(self.sql, condition)

	def execute(self):
		with self.table.parent.cursor_manager() as cursor:
			if 'SELECT' in self.sql or 'DELETE' in self.sql or 'CREATE' in self.sql:
				cursor.execute(self.sql)
			elif self.table.data:
				cursor.executemany(self.sql, self.table.data.to_list_of_dicts())

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


class Select(Statement):
	def __init__(self, table, *columns):
		super().__init__(table)
		self.sql = 'SELECT '
		if not columns:
			self.sql = '{} *, '.format(self.sql)
		for column in columns:
			self.sql = '{}{}, '.format(self.sql, column.name)
		self.sql = '{} FROM {}'.format(self.sql[:-2], self.table.name)

	def where(self, *conditions):
		return Where(self.table, self.sql, *conditions)

	def order_by(self, *columns):
		return OrderBy(self.table, self.sql, *columns)


class Insert(Statement):
	def __init__(self, table):
		super().__init__(table)
		self.sql = 'INSERT INTO {}'.format(self.table.name)
		columns = '('
		values = '('
		for column in self.table.columns:
			# noinspection PyProtectedMember
			if not column._ignore:
				columns = '{}{}, '.format(columns, column.name)
				values = '{}%({})s, '.format(values, column.name)
		self.sql = '{} {}) VALUES {});'.format(self.sql, columns[:-2], values[:-2])


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
	def __init__(self, table, cascaded=False):
		super().__init__(table)
		self.sql = 'DROP TABLE {}'.format(self.table.name)
		if cascaded:
			self.sql = '{} CASCADED;'.format(self.sql)

	def where(self, *conditions):
		return Where(self.table, 'DELETE FROM {}'.format(self.table.name), *conditions)


class Where(Statement):
	def __init__(self, table, sql, *conditions):
		super().__init__(table)
		self.sql = sql
		self.compose(*conditions)

	def order_by(self, *columns):
		return OrderBy(self.table, self.sql, *columns)


class OrderBy(Statement):
	def __init__(self, table, sql, *columns):
		super().__init__(table)
		self.sql = '{} ORDER BY '.format(sql)
		for column in columns:
			self.sql = '{} {}, '.format(self.sql, column.name)
			if column.desc:
				self.sql = '{} DESC, '.format(self.sql[:-2])
		self.sql = '{}'.format(self.sql[:-2])


class Tuple(Statement):
	def __init__(self, table, *columns):
		super().__init__(table)
		for column in columns:
			print(column.name)
		self.sql = '({})'.format(', '.join(column.name for column in columns))

	def in_(self, iterable):
		return Condition('{} {}'.format(self.sql, In(iterable)))
