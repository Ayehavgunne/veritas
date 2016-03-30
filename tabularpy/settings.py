id_headers = [
	'Spid',
	'spid',
	'bill_payment_tran_id',
	'bill payment tran id',
	'cart_item_id',
	'cart item id',
	'call_flow_id',
	'call flow id',
	'acct_num',
	'acct num',
	'user_id',
	'user id',
	'payment_review_id',
	'payment review id'
]


class Settings(object):
	def __init__(
		self, ignore_none=False, datetime_format='%m/%d/%y %I:%M %p', date_format='%m/%d/%y', time_format='%H:%M:%S',
		header_formatter=None, label_formatter=None, cell_formatter=None, sort_headers=False, int_comma=True,
		dont_format=()
	):
		self.ignore_none = ignore_none
		self.datetime_format = datetime_format
		self.date_format = date_format
		self.time_format = time_format
		self.header_formatter = header_formatter
		self.label_formatter = label_formatter
		self.cell_formatter = cell_formatter
		self.sort_headers = sort_headers
		self.int_comma = int_comma
		self.dont_format = list(dont_format) + id_headers
