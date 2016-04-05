from .results import Results
try:
	import psycopg2
except ImportError:
	psycopg2 = None


if psycopg2:
	# noinspection PyCallByClass,PyTypeChecker
	class TableCursor(psycopg2.extensions.cursor):
		def __init__(self, *args, **kwargs):
			super().__init__(*args, **kwargs)
			self.results = None
			self.database = None

		def execute(self, sql, args=None):
			self.results = Results(self, self.database)
			psycopg2.extensions.cursor.execute(self, sql, args)

		def fetchall(self):
			self.results.fill_buffer(psycopg2.extensions.cursor.fetchall(self))
			return self.results

		def scalar(self):
			return psycopg2.extensions.cursor.fetchone(self)[0]
