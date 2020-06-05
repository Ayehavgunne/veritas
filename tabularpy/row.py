import inspect
from decimal import Decimal

from tabularpy import Settings
from tabularpy import cell as c


class Row(object):
    __slots__ = (
        "cells",
        "headers",
        "column_types",
        "row_num",
        "_parent",
        "_i",
        "_settings",
    )

    def __init__(self, cells, headers, column_types, row_num, parent, settings=None):
        self.cells = cells
        self.headers = headers
        self.column_types = column_types
        self.row_num = row_num
        self._parent = parent
        self._settings = settings or Settings()
        self._i = 0

    def index(self, item):
        return self.cells.index(item)

    def get(self, column, default=None):
        if column in self.headers:
            return self[column].value
        else:
            return default

    def format_cells(self, cell_formatter):
        arg_len = len(inspect.signature(cell_formatter).args)
        if arg_len == 1:
            self.cells = [cell_formatter(cell) for header, cell in self.cells]
        elif arg_len == 2:
            self.cells = [
                cell_formatter(cell, self.column_types(header))
                for header, cell in zip(self.headers, self.cells)
            ]
        elif arg_len == 3:
            self.cells = [
                cell_formatter(cell, self.column_types(header), header)
                for header, cell in zip(self.headers, self.cells)
            ]

    def to_dict(self):
        return {header: self.get_cell(header).value for header in self.headers}

    def to_tuple(self):
        tpl = []
        for key, value in self.to_dict().items():
            tpl.append((key, value))
        return tuple(tpl)

    def to_list(self):
        return [self.get_cell(header).value for header in self.headers]

    def keys(self):
        return self.headers

    def sum(self):
        return sum(
            [
                Decimal(str(cell).replace(",", ""))
                for cell in self.cells
                if cell != "" and cell is not None
            ]
        )

    def replace(self, old, new):
        for x, cell in enumerate(self.cells):
            self.cells[x] = c.Cell(
                self.cells[x], self.headers[x], self.row_num, x, self, self._settings
            ).replace(old, new)

    def get_cell(self, x):
        if isinstance(x, str):
            index = self.headers.index(x)
            return c.Cell(
                self.cells[index], x, self.row_num, index, self, self._settings
            )
        elif isinstance(x, int):
            header = self.headers[x]
            return c.Cell(self.cells[x], header, self.row_num, x, self, self._settings)

    def to_html(self, add_attr=None, row_total=False):
        if add_attr:
            html = "".join(
                [
                    f"<td {add_attr(cell, self.column_types[self.headers[x]], self.headers[x], self)}>{self.get_cell(x)}</td>"
                    for x, cell in enumerate(self.cells)
                ]
            )
        else:
            html = "".join(
                [f"<td>{self.get_cell(x)}</td>" for x in range(len(self.cells))]
            )
        if row_total:
            html = f'{html}<td class="rowtotal">{self.sum():,}</td>'
        return html

    def __iter__(self):
        return self

    def __next__(self):
        if self._i < len(self.cells):
            cell = self.get_cell(self._i)
            self._i += 1
            return cell
        else:
            self._i = 0
            raise StopIteration

    def __getattr__(self, item):
        if item in self.headers:
            idx = self.headers.index(item)
            return self.get_cell(idx)
        raise AttributeError(f"attribute {item} does not exist")

    def __getitem__(self, item):
        if isinstance(item, str):
            if item in self.headers:
                idx = self.headers.index(item)
                return self.get_cell(idx)
        elif isinstance(item, int):
            return self.get_cell(item)
        else:
            raise TypeError(f"Cannot access items with type {type(item)}")
        raise ValueError(f"Row does not have item {item}")

    def __setitem__(self, key, value):
        if isinstance(key, c.Cell):
            key = key.value
        if isinstance(value, c.Cell):
            value = value.value
        if isinstance(key, str):
            if key in self.headers:
                self.cells[self.headers.index(key)] = value
                if self._parent:
                    self._parent.change_cell(key, self.row_num, value)
            else:
                raise KeyError(f"'{key}'")
        elif isinstance(key, int):
            if key < len(self.cells):
                self.cells[key] = value
                if self._parent:
                    self._parent.change_cell(self.headers[key], self.row_num, value)
            else:
                raise IndexError("assignment index out of range")
        else:
            raise TypeError(f"indices must be integers or strings, not {type(key)}")

    def __delitem__(self, item):
        if isinstance(item, str):
            if item in self.headers:
                del self.cells[self.headers.index(item)]
                del self.headers[self.headers.index(item)]
        elif isinstance(item, int):
            del self.headers[item]
            del self.cells[item]

    def __contains__(self, item):
        if isinstance(item, str):
            if item in self.headers:
                return True
            else:
                return False
        elif isinstance(item, int):
            if item in self.cells:
                return True
            else:
                return False

    def __eq__(self, other):
        if self.cells != other.cells:
            return False
        if self.headers != other.headers:
            return False
        return True

    def __len__(self):
        return len(self.cells)

    def __str__(self):
        return str(self.cells)

    def __repr__(self):
        return f"<{type(self).__name__} Cells: {self.cells}>"
