from tabularpy.row import Row


class Results(object):
    def __init__(self, table):
        self.table = table
        self._i = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._i < len(self.table.results_buffer):
            row = self.table.results_buffer[self._i]
            row = Row(
                list(row),
                list(self.table.get_column_names()),
                self.table.get_column_types(),
                self._i,
                self.table
            )
            self._i += 1
            return row
        else:
            self._i = 0
            raise StopIteration
