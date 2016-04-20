import cgitb
from .operators import And
from .operators import Or
from .operators import Not
from . import postgres
from .statements import TableCopy
from .table import Table


# TODO: Add ability to create temp tables based on other tables and copy information between them
class Database(object):
	def __init__(self, connection=None, log=None):
		self.connection = connection
		self.tables = []
		if log:
			self.log = log
		else:
			import logging
			self.log = logging.getLogger('sql_manager_dummy')
			self.log.info('Initializing Sql Manager')
		self.name = None
		self.t = None
		self.type_ = None

	def reflect(self, name=None):
		if name:
			if not self.has_table(name):
				self.tables.append(Table(name, self))
				self.tables[-1].reflect()
		else:
			for name in self.get_table_names():
				if not self.has_table(name):
					self.tables.append(Table(name, self))
					self.tables[-1].reflect()
		self.t = Tables(self.tables)

	def get_name(self):
		with self.cursor_manager() as cursor:
			cursor.execute('SELECT current_database();')
			name = cursor.fetchone()[0]
			return name

	def get_table(self, name):
		for table in self.tables:
			if table.name == name:
				return table

	def get_table_names(self):
		with self.cursor_manager() as cursor:
			# noinspection SqlResolve
			cursor.execute(
				"SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name"
			)
			results = cursor.fetchall()
			names = tuple(table[0] for table in results)
			return names

	def get_current_seq_val(self, name):
		with self.cursor_manager() as cursor:
			# noinspection SqlResolve
			cursor.execute('SELECT last_value FROM {};'.format(name))
			seq_val = cursor.fetchone()[0]
			return seq_val

	def get_next_seq_val(self, name):
		with self.cursor_manager() as cursor:
			# noinspection SqlResolve
			cursor.execute("SELECT nextval('{}');".format(name))
			seq_val = cursor.fetchone()[0]
			return seq_val

	def add_table(self, table):
		table.parent = self
		self.tables.append(table)
		self.t = Tables(self.tables)

	def remove_table(self, name):
		if self.has_table(name):
			self.tables.remove(self.get_table(name))

	@staticmethod
	def copy_between_tables(from_table, to_table, *columns):
		return TableCopy(from_table, to_table, *columns)

	@staticmethod
	def and_(*conditions):
		return And(*conditions)

	@staticmethod
	def or_(*conditions):
		return Or(*conditions)

	@staticmethod
	def not_(condition):
		return Not(condition)

	def pg_connect(self, connection_string):
		try:
			# noinspection PyUnresolvedReferences
			import psycopg2
			self.connection = psycopg2.connect(connection_string, cursor_factory=postgres.TableCursor)
			self.name = self.get_name()
			self.type_ = 'PostgreSQL'
		except ImportError:
			raise ImportError('Psycopg2 must be installed to create a PostgreSql connection')

	def get_cursor(self):
		return self.connection.cursor()

	def cursor_manager(self):
		return cursormanager(self)

	def commit(self):
		self.connection.commit()

	def rollback(self):
		self.connection.rollback()

	def close(self):
		self.connection.close()

	def has_table(self, name):
		for table in self.tables:
			if table.name == name:
				return True
		return False

	def __str__(self):
		return 'CREATE DATABASE {};\n\n{}'.format(self.name, '\n\n'.join(str(table) for table in self.tables))


class Tables(object):
	def __init__(self, tables):
		self.tables = tables

	def __getattr__(self, item):
		return self._get(item)

	def __getitem__(self, item):
		return self._get(item)

	def _get(self, item):
		for table in self.tables:
			if item == table.name:
				return table
		raise AttributeError


class cursormanager(object):
	def __init__(self, database):
		self.database = database
		self.cursor = None

	def __enter__(self):
		self.cursor = self.database.connection.cursor()
		self.cursor.database = self.database
		return self.cursor

	def __exit__(self, exc_type, exc_val, exc_tb):
		# noinspection PyBroadException
		try:
			if exc_type or exc_val or exc_tb:
				self.database.log.error(cgitb.text((exc_type, exc_val, exc_tb)))
				self.database.rollback()
			else:
				if self.database.type_ == 'PostgreSQL':
					self.cursor.fetchall()
				else:
					self.database.results_buffer = self.cursor.fetchall()
		except Exception:
			pass
		finally:
			self.cursor.close()
			self.database.commit()
