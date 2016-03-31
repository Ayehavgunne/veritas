import copy
import re
from pathlib import Path
from collections import defaultdict
from collections import OrderedDict
from html.parser import HTMLParser
from datetime import datetime
from datetime import timedelta


def minimum(x):
	raise NotImplementedError(x)


def maximum(x):
	raise NotImplementedError(x)


def product(x):
	raise NotImplementedError(x)


def count(x):
	raise NotImplementedError(x)


def avg(x):
	raise NotImplementedError(x)


def sum_aggr(x):
	return sum(x)


def get_sql_query_types(query):
	t = OrderedDict()
	for column in query.column_descriptions:
		t[column['name']] = column['type']
	return t


def seconds_since_epoch(date_time):
	return (date_time - datetime(1970, 1, 1)).total_seconds()


def getitem(obj, index, default=None):
	try:
		value = obj[index]
		return value if value is not None else default
	except IndexError:
		return default


def getindex(obj, item, default=0):
	try:
		return obj.index(item)
	except ValueError:
		return default


def getindexes(obj, item):
	indexes = []
	for i, val in enumerate(obj):
		if val == item:
			indexes.append(i)
	return indexes


def rotate_clockwise(matrix, degree=90):
	if degree not in [0, 90, 180, 270, 360]:
		return
	return matrix if not degree else rotate_clockwise(zip(*list(matrix)[::-1]), degree - 90)


def horizontal_matrix_flip(matrix):
	return [list(reversed(row)) for row in matrix]


def transpose(matrix):
	return horizontal_matrix_flip(rotate_clockwise(matrix))


def find_duplicates(lst):
	temp = defaultdict(list)
	dups = {}
	for i, e in enumerate(lst):
		temp[e].append(i)
	for k, v in temp.items():
		if len(v) >= 2:
			dups[k] = v
	return dups


def merge_sort(array, index, key=None, reverse=False):
	size = len(array)
	if size < 2:
		return array
	if not key:
		key = lambda x: x
	middle = size // 2
	left = merge_sort(array[:middle], index, key, reverse)
	right = merge_sort(array[middle:], index, key, reverse)
	left.reverse()
	right.reverse()
	result = []
	while left and right:
		if not reverse:
			if key(left[-1][index]) <= key(right[-1][index]):
				result.append(left.pop())
			else:
				result.append(right.pop())
		else:
			if key(left[-1][index]) >= key(right[-1][index]):
				result.append(left.pop())
			else:
				result.append(right.pop())
	left.reverse()
	right.reverse()
	if left:
		result.extend(left)
	if right:
		result.extend(right)
	return result


def datetime_to_quarter(date_time):
	return 'Q%s %s' % ((date_time.month - 1) // 3 + 1, date_time.year)


def parse_time_delta(s):
	if isinstance(s, str):
		if s == '0':
			return timedelta()
		if s is None:
			return None
		d = re.search(r'((?P<days>\d+) )?(?P<hours>\d+):(?P<minutes>\d+):(?P<seconds>\d+).(?P<deciseconds>\d+)', s)
		if d is None:
			print(s, 'could not be parsed')
			return None
		d = d.groupdict(0)
		seconds = 0.0
		if 'days' in d:
			seconds += int(d['days']) * 86400
		if 'hours' in d:
			seconds += int(d['hours']) * 3600
		if 'minutes' in d:
			seconds += int(d['minutes']) * 60
		if 'seconds' in d:
			seconds += int(d['seconds'])
		if 'deciseconds' in d:
			seconds += float('.{}'.format(d['deciseconds']))
		return timedelta(seconds=seconds)
	return s


def parse_date_time_string(value, str_format):
	if isinstance(value, str):
		try:
			# noinspection PyUnresolvedReferences
			from dateutil.parser import parse
			value = parse(value)
		except ImportError:
			value = datetime.strptime(value, str_format)
	return value


class HtmlParser(HTMLParser):
	__slots__ = [
		'html', '_open_tags', '_open_tag_attrs', '_relevant_tags',
		'_row_num', '_col_num', '_data', '_hidden_rows', '_td'
	]

	def __init__(self):
		super().__init__()
		self._open_tags = []
		self._open_tag_attrs = []
		self._relevant_tags = ('table', 'thead', 'tbody', 'tfoot', 'tr', 'th', 'td')
		self._row_num = -1
		self._col_num = -1
		self._data = []
		self._hidden_rows = []
		self._td = {'table': {}, 'headers': [], 'footers': [], 'column_types': {}}

	def parse(self, html):
		self.reset()
		self.feed(html)
		return self._td

	def handle_starttag(self, tag, attrs):
		if tag in self._relevant_tags:
			self._open_tags.append(tag)
			self._open_tag_attrs.append({key: value for key, value in attrs})
			if 'tbody' in self._open_tags:
				if tag == 'tr':
					self._row_num += 1
					self._col_num = -1
				elif tag == 'td':
					self._col_num += 1

	def handle_endtag(self, tag):
		if tag in self._relevant_tags:
			last_open_tag = self._open_tags[-1]
			last_open_attrs = self._open_tag_attrs[-1]
			if 'tr' == last_open_tag:
				for attr in last_open_attrs.values():
					if 'display: none' in attr:
						self._hidden_rows.append(self._row_num)
			if 'thead' in self._open_tags:
				if 'th' == last_open_tag:
					self._data = ''.join(self._data)
					if self._data == '':
						self._data = str(self._col_num)
					self._td['headers'].append(self._data)
					self._td['table'][self._data] = []
					self._data = []
			elif 'tfoot' in self._open_tags:
				if 'th' == last_open_tag:
					self._data = ''.join(self._data)
					self._td['footers'].append(self._data)
					self._data = []
			elif 'tbody' in self._open_tags:
				if 'td' == last_open_tag:
					header = self._td['headers'][self._col_num]
					self._data = ''.join(self._data)
					self._td['table'][header].append(self._data)
					if header not in self._td['column_types']:
						self._td['column_types'][header] = last_open_attrs
					self._data = []
			if tag == last_open_tag:
				self._open_tags.pop()  # poppin tags :)
				self._open_tag_attrs.pop()

	def handle_data(self, data):
		self._data.append(data.strip())

	def handle_charref(self, ref):
		self.handle_entityref("#" + ref)

	def handle_entityref(self, ref):
		# noinspection PyDeprecation
		self.handle_data(self.unescape("&{};".format(ref)))

	def error(self, message):
		print(message)


class BeautifulSoupParser(object):
	def __init__(self, parser='html.parser'):
		self.soup = None
		self.parser = parser

	def parse(self, html):
		try:
			# noinspection PyUnresolvedReferences
			from bs4 import BeautifulSoup
		except ImportError:
			print('Need to install BeautifulSoup4 or use the standard HTML Parser')
			raise
		td = {'table': {}, 'headers': [], 'footers': [], 'column_types': {}}
		self.soup = BeautifulSoup(html, self.parser)
		self.normalize_html()
		table = self.soup.find('table')
		for x, header in enumerate(table.find('thead').find('tr').find_all('th')):
			if header.text == '':
				td['headers'].append(str(x))
				td['table'][str(x)] = []
				td['column_types'][str(x)] = 'string'
			else:
				td['headers'].append(header.text)
				td['table'][header.text] = []
		first = True
		for row in table.find('tbody').find_all('tr'):
			if not ('style' in row.attrs and 'display:none' in row.attrs['style'].replace(' ', '')):
				for x, cell in enumerate(row.find_all('td')):
					td['table'][td['headers'][x]].append(cell.text)
					if first and 'class' in cell.attrs:
						td['column_types'][td['headers'][x]] = cell.attrs['class'][0]
					elif first:
						td['column_types'][td['headers'][x]] = 'string'
				first = False
		if table.find('tfoot') and table.find('tfoot').find('tr'):
			for footer in table.find('tfoot').find('tr').find_all('th'):
				td['footers'].append(footer.text)
		return td

	def normalize_html(self):
		table = self.soup.find('table')
		header_trs = table.find_all('tr')
		while table.find(colspan=True) or table.find(rowspan=True):
			self.clean_spans()
		if not table.find('thead'):
			header_trs[0].wrap(self.soup.new_tag('thead'))
		for th in table.find('thead').find_all('td'):
			th.name = 'th'
		if not table.find('tbody'):
			tbody_trs = table.find_all('tr', recursive=False)
			tbody_trs_list = []
			for tbody_tr in tbody_trs:
				tbody_trs_list.append(tbody_tr.extract())
			table.append(self.soup.new_tag('tbody'))
			for tbody_tr in tbody_trs_list:
				table.find('tbody').append(tbody_tr)
		for th in table.find('tbody').find_all('th'):
			th.name = 'td'
		if table.find('tfoot'):
			for th in table.find('tfoot').find_all('td'):
				th.name = 'th'

	def clean_spans(self):
		header_trs = self.soup.find('table').find_all('tr')
		for x, tr in enumerate(header_trs):
			cells = tr.select('th, td')
			for y, ele in enumerate(cells):
				if ele.has_attr('colspan'):
					colspan = int(ele.attrs.pop('colspan'))
					if colspan > 1:
						new_tag = self.soup.new_tag(ele.name)
						new_tag.string = ele.text
						new_tag.attrs = ele.attrs
						for _ in range(1, colspan):
							tr.insert(y, copy.copy(new_tag))
				if ele.has_attr('rowspan'):
					rowspan = int(ele.attrs.pop('rowspan'))
					if rowspan > 1:
						new_tag = self.soup.new_tag(ele.name)
						new_tag.string = ele.text
						new_tag.attrs = ele.attrs
						for z in range(1, rowspan):
							self.soup.find_all('tr')[x + z:x + z + 1][0].insert(y, copy.copy(new_tag))


def open_xls_as_xlsx(filename):
	try:
		# noinspection PyUnresolvedReferences
		import xlrd
		# noinspection PyUnresolvedReferences
		from openpyxl.workbook import Workbook
		# noinspection PyUnresolvedReferences
		from openpyxl.reader.excel import load_workbook

		book = xlrd.open_workbook(filename)
		index = 0
		nrows, ncols = 0, 0
		sheet = None
		while nrows * ncols == 0:
			sheet = book.sheet_by_index(index)
			nrows = sheet.nrows
			ncols = sheet.ncols
			index += 1
		book1 = Workbook()
		sheet1 = book1.get_active_sheet()
		for row in range(0, nrows):
			for col in range(0, ncols):
				sheet1.cell(row=row + 1, column=col + 1).value = sheet.cell_value(row, col)
		filename = filename.replace('.xls', '.xlsx')
		book1.save(filename)
		return Path(filename)
	except ImportError:
		print('xlrd and openpyxl are required in order to convert an xls file to xlsx')
		raise

# noinspection SqlResolve
select_column_names_sql = '''SELECT
	a.attname AS column_name
FROM
	pg_class c,
	pg_attribute a
WHERE
	c.relname = '{}' AND
	a.attnum > 0 AND
	a.attrelid = c.oid AND
	a.attname NOT LIKE '%pg.dropped%'
ORDER BY a.attname;'''

# noinspection SqlResolve
select_types_sql = '''SELECT
	column_name,
	UPPER(type)
FROM (
	SELECT
		a.attname AS column_name,
		pg_catalog.format_type(a.atttypid, a.atttypmod) AS type
	FROM
		pg_class c,
		pg_attribute a,
		pg_type t
	WHERE
		c.relname = '{}' AND
		a.attnum > 0 AND
		a.attrelid = c.oid AND
		a.atttypid = t.oid
	ORDER BY a.attnum
) AS tabledefinition;'''

# noinspection SqlResolve
select_not_nullable_sql = '''SELECT
	a.attname AS column_name
FROM
	pg_class c,
	pg_attribute a
WHERE
	c.relname = '{}' AND
	a.attnum > 0 AND
	a.attrelid = c.oid AND
	a.attnotnull
ORDER BY a.attnum;'''

# noinspection SqlResolve
select_pkey_sql = '''SELECT
	a.attname
FROM
	pg_index AS i
JOIN
	pg_attribute a ON a.attrelid = i.indrelid AND
	a.attnum = ANY(i.indkey)
WHERE
	i.indrelid = '{}'::regclass AND
	i.indisprimary;'''

# noinspection SqlResolve
select_serial_sql = '''WITH sequences AS (
	SELECT
		oid,
		relname AS sequencename
	FROM
		pg_class
	WHERE
		relkind = 'S'
)
SELECT
	col.attname AS columnname,
	seqs.sequencename
FROM
	pg_attribute col
JOIN
	pg_class tab ON col.attrelid = tab.oid
JOIN
	pg_namespace sch ON tab.relnamespace = sch.oid
LEFT JOIN
	pg_attrdef def ON tab.oid = def.adrelid AND
	col.attnum = def.adnum
LEFT JOIN
	pg_depend deps ON def.oid = deps.objid AND
	deps.deptype = 'n'
LEFT JOIN
	sequences seqs ON deps.refobjid = seqs.oid
WHERE
	tab.relname = '{}' AND
	sch.nspname != 'information_schema' AND
	sch.nspname NOT LIKE 'pg_%' AND
	col.attnum > 0 AND
	seqs.sequencename IS NOT NULL
ORDER BY
	col.attname;'''

# noinspection SqlResolve
select_index_sql = '''SELECT
	a.attname
FROM
	pg_index AS i
JOIN
	pg_attribute a ON a.attrelid = i.indrelid AND
	a.attnum = ANY(i.indkey)
WHERE
	i.indrelid = '{}'::regclass AND
	NOT i.indisprimary;'''

# noinspection SqlResolve
select_contraints_sql = '''SELECT
	kcu.column_name,
	tc.constraint_type
FROM
	information_schema.table_constraints AS tc
LEFT JOIN
	information_schema.key_column_usage AS kcu
	ON tc.constraint_catalog = kcu.constraint_catalog AND
	tc.constraint_schema = kcu.constraint_schema AND
	tc.constraint_name = kcu.constraint_name
WHERE
	tc.table_name = '{}' AND
	kcu.column_name IS NOT NULL;'''
