import cgitb
from .table import Table
from .conditions import And
from .conditions import Not
from .conditions import Or

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
		self.cursor = None
		self.t = None
		self.results_buffer = None

	def reflect(self, name=None):
		if name:
			self.tables.append(Table(name, self))
			self.tables[-1].reflect()
		else:
			for name in self.get_table_names():
				self.tables.append(Table(name, self))
				self.tables[-1].reflect()
		self.t = Tables(self.tables)

	def get_name(self):
		with self.cursor_manager() as cursor:
			cursor.execute('SELECT current_database();')
			return cursor.fetchone()[0]

	def table_exists(self, name):
		for table in self.tables:
			if name == table.name:
				return True
		return False

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
			return tuple(table[0] for table in cursor.fetchall())

	def add_table(self, table):
		table.parent = self
		self.tables.append(table)
		self.t = Tables(self.tables)

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
			self.connection = psycopg2.connect(connection_string)
			self.name = self.get_name()
		except ImportError:
			raise ImportError('Psycopg2 must be installed to create a PostgreSql cursor')

	def cursor_manager(self):
		return cursormanager(self)

	def get_cursor(self):
		return self.connection.cursor()

	def commit(self):
		self.connection.commit()

	def close(self):
		if self.cursor:
			self.cursor.close()
		self.connection.close()

	def __str__(self):
		return 'CREATE DATABASE {};\n\n{}'.format(self.name, '\n\n'.join(str(table) for table in self.tables))


class cursormanager(object):
	def __init__(self, database):
		self.database = database
		self.cursor = None

	def __enter__(self):
		self.cursor = self.database.connection.cursor()
		self.database.cursor = self.cursor
		return self.cursor

	def __exit__(self, exc_type, exc_val, exc_tb):
		# noinspection PyBroadException
		try:
			if exc_type or exc_val or exc_tb:
				self.database.log.error(cgitb.text((exc_type, exc_val, exc_tb)))
				self.database.connection.rollback()
			else:
				self.database.results_buffer = self.cursor.fetchall()
		except Exception:
			pass
		finally:
			self.database.cursor = None
			self.cursor.close()
			self.database.commit()

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
