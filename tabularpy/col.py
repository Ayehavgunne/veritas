from decimal import Decimal

from tabularpy import Settings
from tabularpy import cell as cell_module


class Col(object):
    __slots__ = (
        "cells",
        "column_type",
        "header",
        "col_num",
        "_parent",
        "_i",
        "_settings",
    )

    def __init__(self, cells, column_type, header, col_num, parent, settings=None):
        self.cells = cells
        self.column_type = column_type
        self.header = header
        self.col_num = col_num
        self._parent = parent
        self._settings = settings or Settings()
        self._i = 0

    def index(self, item):
        return self.cells.index(item)

    def get(self, row, default=None):
        if row < self._parent.num_rows:
            return self[row].value
        else:
            return default

    def to_list(self):
        return self.cells

    def is_numeric(self):
        if self.column_type.lower() in [
            "integer",
            "decimal",
            "float",
            "percent",
            "money",
        ]:
            return True
        else:
            return False

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
            self.cells[x] = cell_module.Cell(
                cell, self.header, x, self.col_num, self, self._settings
            ).replace(old, new)

    def get_cell(self, x):
        return cell_module.Cell(
            self.cells[x], self.header, x, self.col_num, self, self._settings
        )

    def to_html(self, add_attr=None, row_total=False):
        if add_attr:
            html = "".join(
                [
                    f"<td {add_attr(cell, self.column_type, x, self)}>"
                    f"{self.get_cell(x)}</td>"
                    for x, cell in enumerate(self.cells)
                ]
            )
        else:
            html = "".join([f"<td>{cell}</td>" for cell in self.cells])
        if row_total:
            html = f'{html}<td class="rowtotal">{self.sum():,}</td>'
        return html

    def __next__(self):
        if self._i < len(self.cells):
            cell = self.get_cell(self._i)
            self._i += 1
            return cell
        else:
            self._i = 0
            raise StopIteration

    def __getitem__(self, item):
        return self.get_cell(item)

    def __setitem__(self, key, value):
        if isinstance(key, cell_module.Cell):
            key = key.value
        if isinstance(value, cell_module.Cell):
            value = value.value
        if isinstance(key, int):
            if key < len(self.cells):
                self.cells[key] = value
                if self._parent:
                    self._parent.change_cell(self.header, key, value)
            else:
                raise IndexError("assignment index out of range")
        else:
            raise TypeError(f"indices must be integers, not {type(key)}")

    def __delitem__(self, item):
        del self.cells[item]

    def __contains__(self, item):
        if item in self.cells:
            return True
        else:
            return False

    def __eq__(self, other):
        if self.cells != other.cells:
            return False
        return True

    def __len__(self):
        return len(self.cells)

    def __str__(self):
        return str(self.cells)

    def __repr__(self):
        return f"<{type(self).__name__} Cells: {self.cells}>"
