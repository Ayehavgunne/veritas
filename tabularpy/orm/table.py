from .column import Column
from . import statements
from .types import Varchar
from .types import BigInt
from .types import Percent
from .types import Integer
from .types import Numeric
from .types import Money
from .types import Boolean
from .types import Date
from .types import Timestamp
from .types import Time
from .types import Interval
from ..util import select_column_names_sql
from ..util import select_serial_sql
from ..util import select_types_sql
from ..util import select_pkey_sql
from ..util import select_index_sql
from ..util import select_not_nullable_sql
from ..util import select_contraints_sql


# TODO: Add join statments
class Table(object):
	def __init__(self, name, parent):
		self.name = name
		self.parent = parent
		self.columns = []
		self.primary_keys = []
		self.serials = []
		self.indexes = []
		self.uniques = []
		self.c = None
		self.data = None
		self.results_buffer = []
		self.temp_num = 0

	def reflect(self):
		self.reflect_column_types()
		self.reflect_primary_keys()
		self.reflect_serials()
		self.reflect_indexes()
		self.reflect_not_nullables()
		self.reflect_constraints()
		self.c = Columns(self.columns)

	def reflect_from_data(self):
		if self.data:
			for header in self.data.headers:
				self.columns.append(Column(header, self.data.column_types[header], self, self.parent))

	def get_column_names(self):
		return (column.name for column in self.columns)

	def get_column_types(self):
		return {column.name: column.type_ for column in self.columns}

	def get_pkey_columns(self):
		return (self.get_column(name) for name in self.primary_keys)

	def get_index_columns(self):
		return (self.get_column(name) for name in self.indexes)

	def get_unique_columns(self):
		return (self.get_column(name) for name in self.uniques)

	def query_column_names(self):
		with self.parent.cursor_manager() as cursor:
			cursor.execute(select_column_names_sql.format(self.name))
			return (row[0] for row in cursor.fetchall())

	def query_column_types(self):
		with self.parent.cursor_manager() as cursor:
			cursor.execute(select_types_sql.format(self.name))
			rows = cursor.fetchall()
			return {str(row[0]): row[1] for row in rows}

	def reflect_column_types(self):
		self.columns = []
		for name, col_type in self.query_column_types().items():
			col_type = col_type.lower()
			if 'varchar' in name or 'character varying' in col_type:
				type_ = Varchar()
			elif col_type == 'integer':
				type_ = Integer()
			elif col_type == 'bigint':
				type_ = BigInt()
			elif 'numeric' in col_type:
				type_ = Numeric()
			elif col_type == 'percent':
				type_ = Percent()
			elif col_type == 'money':
				type_ = Money()
			elif col_type == 'boolean':
				type_ = Boolean()
			elif col_type == 'date':
				type_ = Date()
			elif 'timestamp' in col_type:
				type_ = Timestamp()
			elif 'time' in col_type:
				type_ = Time()
			elif col_type == 'interval':
				type_ = Interval()
			else:
				type_ = Varchar()
			self.columns.append(Column(name, type_))

	def query_primary_keys(self):
		with self.parent.cursor_manager() as cursor:
			cursor.execute(select_pkey_sql.format(self.name))
			return (row[0] for row in cursor.fetchall())

	def reflect_primary_keys(self):
		self.primary_keys = list(self.query_primary_keys())

	def query_serials(self):
		with self.parent.cursor_manager() as cursor:
			cursor.execute(select_serial_sql.format(self.name))
			return {str(row[0]): row[1] for row in cursor.fetchall()}

	def reflect_serials(self):
		self.serials = []
		for name, seq in self.query_serials().items():
			self.serials.append(name)
			with self.parent.cursor_manager() as cursor:
				# noinspection SqlResolve
				cursor.execute("SELECT setval('{}', COALESCE((SELECT MAX({})+1 FROM {}), 1), false);".format(seq, name, self.name))
			col = self.get_column(name)
			col.serial = seq
			col.serial_val = self.parent.get_next_seq_val(seq)

	def query_indexes(self):
		with self.parent.cursor_manager() as cursor:
			cursor.execute(select_index_sql.format(self.name))
			return (row[0] for row in cursor.fetchall())

	def reflect_indexes(self):
		self.indexes = list(self.query_indexes())

	def query_not_nullables(self):
		with self.parent.cursor_manager() as cursor:
			cursor.execute(select_not_nullable_sql.format(self.name))
			return (row[0] for row in cursor.fetchall())

	def reflect_not_nullables(self):
		for name in self.query_not_nullables():
			self.get_column(name).nullable = False

	def query_constraints(self):
		with self.parent.cursor_manager() as cursor:
			cursor.execute(select_contraints_sql.format(self.name))
			return {str(row[0]): row[1] for row in cursor.fetchall()}

	def reflect_constraints(self):
		self.uniques = []
		for name, constraint in self.query_constraints().items():
			column = self.get_column(name)
			if constraint == 'UNIQUE':
				column.unique = True
				self.uniques.append(name)
			# TODO: Add more constraint types

	def add_table_data(self, data):
		if self.columns:
			for header in data.headers:
				if not self.has_column(header):
					raise ValueError('Columns do not match')
			self.data = data
			self.data.sql_table = self
			self.data.reflect()
		else:
			self.data = data
			self.data.sql_table = self
			self.reflect_from_data()

	# noinspection PyProtectedMember
	def change_cell(self, x, y, value):
		if isinstance(y, str) and isinstance(x, int):
			if self.has_column(y):
				if self._has_row(x):
					self.data._table_data[y][x] = value
				else:
					raise AttributeError('{} does not have row {}'.format(self, x))
			else:
				raise AttributeError('{} does not have column {}'.format(self, y))
		elif isinstance(y, int) and isinstance(x, int):
			header = self.get_column(y)
			if self._has_row(x):
				self.data._table_data[header][x] = value
			else:
				raise AttributeError('{} does not have row {}'.format(self, x))

	def add_column(self, column):
		column.database = self.parent
		column.parent = self
		self.columns.append(column)
		if column.primary_key:
			self.primary_keys.append(column.name)
		if column.index:
			self.indexes.append(column.name)
		if column.unique:
			self.uniques.append(column.name)
		self.c = Columns(self.columns)

	def add_primary_key(self, name):
		self.primary_keys.append(name)
		self.get_column(name).primary_key = True

	def add_index(self, name):
		self.indexes.append(name)
		self.get_column(name).index = True

	def set_unique(self, name):
		self.uniques.append(name)
		self.get_column(name).unique = True

	def set_not_nullable(self, name):
		self.get_column(name).nullable = False

	def set_column_default(self, name, default):
		self.get_column(name).default = default

	def get_column(self, name):
		for column in self.columns:
			if column.name == name:
				return column

	def column_exists(self, name):
		for column in self.columns:
			if column.name == name:
				return True
		return False

	def create(self):
		return statements.Create(self)

	def create_temp(self):
		temp_table = Table('temp_{}_{}'.format(self.name, self.temp_num), self.parent)
		temp_table.columns = self.columns
		temp_table.c = Columns(temp_table.columns)
		self.parent.add_table(temp_table)
		return statements.CreateTemp(temp_table, self.name)

	def select(self, *columns):
		return statements.Select(self, *columns)

	def insert(self):
		if not self.data:
			raise AttributeError('The table must have data to insert with first')

		return statements.Insert(self)

	def update(self):
		if not self.data:
			raise AttributeError('The table must have data to update with first')
		return statements.Update(self)

	def upsert(self, *on):
		if not self.data:
			raise AttributeError('The table must have data to upsert with first')
		with self.parent.cursor_manager() as cursor:
			if len(on) > 1:
				self.delete(*on).where(self.tuple_(*on).in_(on)).execute(cursor)
			else:
				self.delete(on[0]).where(self.tuple_(on[0]).in_(on)).execute(cursor)
			self.insert().execute(cursor)

	def delete(self, *on, cascaded=False):
		return statements.Delete(self, *on, cascaded)

	def drop(self, cascaded=False):
		return statements.Drop(self, cascaded)

	def copy_from_file(self, absolute_path):
		"""Connected User needs Superuser privlages and access to the server filesystem"""
		return statements.CopyFromFile(self, absolute_path)

	def tuple_(self, *columns):
		return statements.Tuple(self, *columns)

	def has_column(self, name):
		for column in self.columns:
			if column.name == name:
				return True
		return False

	# noinspection PyProtectedMember
	def _has_row(self, row_num):
		if self.data:
			return self.data._has_row(row_num)

	def __str__(self):
		sql = 'CREATE TABLE {} (\n'.format(self.name)
		for column in self.columns:
			sql = '{}\t{},\n'.format(sql, column)
		sql = '{}\n);'.format(sql[:-2])
		if self.primary_keys:
			sql = '{}\nCONSTRAINT {}_pkey PRIMARY KEY ('.format(sql, self.name)
			for pkey in self.primary_keys:
				sql = '{}{}, '.format(sql, pkey)
			sql = '{});'.format(sql[:-2])
		if self.uniques:
			for unique in self.uniques:
				sql = '{0}\nCONSTRAINT {1}_{2}_key UNIQUE ({2});'.format(sql, self.name, unique)
		if self.indexes:
			for index in self.indexes:
				sql = '{0}\nCREATE INDEX {1}_{2}_idx ON {1} USING btree ({2});'.format(sql, self.name, index)
		return sql

	def __repr__(self):
		return 'Table(name={})'.format(self.name)

	def __hash__(self):
		return hash(repr(self))


class Columns(object):
	def __init__(self, columns):
		self.columns = columns

	def __getattr__(self, item):
		return self._get(item)

	def __getitem__(self, item):
		return self._get(item)

	def _get(self, item):
		for column in self.columns:
			if item == column.name:
				return column
		raise AttributeError
