class Settings:
    def __init__(
        self,
        ignore_none=False,
        datetime_format="%m/%d/%y %I:%M %p",
        date_format="%m/%d/%y",
        time_format="%H:%M:%S",
        header_formatter=None,
        cell_formatter=None,
        sort_headers=False,
        int_comma=True,
        dec_comma=True,
        float_comma=True,
        divide_percent=True,
        dont_format=(),
        empty_string_is_none=False,
        clean_values=True,
        do_not_guess_types=False,
    ):
        self.ignore_none = ignore_none
        self.datetime_format = datetime_format
        self.date_format = date_format
        self.time_format = time_format
        self.header_formatter = header_formatter
        self.cell_formatter = cell_formatter
        self.sort_headers = sort_headers
        self.int_comma = int_comma
        self.dec_comma = dec_comma
        self.float_comma = float_comma
        self.divide_percent = divide_percent
        self.dont_format = list(dont_format)
        self.empty_string_is_none = empty_string_is_none
        self.clean_values = clean_values
        self.do_not_guess_types = do_not_guess_types
