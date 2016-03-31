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

ignore_none_default = False
datetime_format_default = '%m/%d/%y %I:%M %p'
date_format_default = '%m/%d/%y'
time_format_default = '%H:%M:%S'
header_formatter_default = None
label_formatter_default = None
cell_formatter_default = None
sort_headers_default = False
int_comma_default = True
dec_comma_default = True
float_comma_default = True


class Settings(object):
	def __init__(
		self, ignore_none=ignore_none_default, datetime_format=datetime_format_default, date_format=date_format_default,
		time_format=time_format_default, header_formatter=header_formatter_default, label_formatter=label_formatter_default,
		cell_formatter=cell_formatter_default, sort_headers=sort_headers_default, int_comma=int_comma_default,
		dec_comma=dec_comma_default, float_comma=float_comma_default, dont_format=()
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
		self.dec_comma = dec_comma
		self.float_comma = float_comma
		self.dont_format = list(dont_format) + id_headers
