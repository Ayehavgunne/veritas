import locale
from decimal import InvalidOperation

from tabularpy import Settings, tables

from . import col, row
from .util import cast, clean_value, format_value

locale.setlocale(locale.LC_ALL, "")


class Cell(object):
    __slots__ = (
        "_value",
        "_raw_value",
        "header",
        "row_num",
        "col_num",
        "column_type",
        "_parent",
        "_settings",
        "_i",
    )

    def __init__(
        self,
        value,
        header=None,
        row_num=None,
        col_num=None,
        parent=None,
        settings=None,
        column_type=None,
    ):
        self.header = header
        self.row_num = row_num
        self.col_num = col_num
        self._parent = parent
        if not column_type:
            if isinstance(self._parent, row.Row):
                self.column_type = self._parent.column_types[self.header]
            elif isinstance(self._parent, col.Col):
                self.column_type = self._parent.column_type
            elif isinstance(self._parent, tables.BaseTable):
                self.column_type = self._parent.column_types[self.header]
        else:
            self.column_type = column_type
        self._settings = settings or Settings()
        try:
            self._value = clean_value(value, self.column_type, settings)
            self._raw_value = value
        except (TypeError, InvalidOperation):
            self._value = value
        self._i = 0

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_val):
        self._raw_value = new_val
        self._value = clean_value(new_val, self.column_type, self._settings)

    @property
    def raw_value(self):
        return self._raw_value

    def replace(self, old, new):
        if isinstance(self.value, str):
            return self._new(self.value.replace(old, new))

    def _new(self, value, cell_type=None):
        if not cell_type:
            cell_type = cast(value)
            if not cell_type:
                cell_type = self.column_type
            return Cell(
                value,
                self.header,
                self.row_num,
                self.col_num,
                self._parent,
                self._settings,
                cell_type,
            )
        else:
            return Cell(
                value,
                self.header,
                self.row_num,
                self.col_num,
                self._parent,
                self._settings,
                cell_type,
            )

    def __setattr__(self, key, value):
        if key == "value":
            if self._parent:
                if isinstance(self._parent, row.Row):
                    self._parent[self.header] = value
                elif isinstance(self._parent, col.Col):
                    self._parent[self.row_num] = value
                elif isinstance(self._parent, tables.BaseTable):
                    self._parent[self.header][self.row_num] = value
        object.__setattr__(self, key, value)

    def __eq__(self, other):
        if isinstance(other, Cell):
            return self.value == other.value
        else:
            return self.value == other

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        if isinstance(other, Cell):
            return self.value < other.value
        else:
            return self.value < other

    def __le__(self, other):
        if isinstance(other, Cell):
            return self.value <= other.value
        else:
            return self.value <= other

    def __gt__(self, other):
        if isinstance(other, Cell):
            return self.value > other.value
        else:
            return self.value > other

    def __ge__(self, other):
        if isinstance(other, Cell):
            return self.value >= other.value
        else:
            return self.value >= other

    def __bool__(self):
        return bool(self.value)

    def __add__(self, other):
        if isinstance(other, Cell):
            return self._new(self.value + other.value)
        else:
            return self._new(self.value + other)

    def __sub__(self, other):
        if isinstance(other, Cell):
            return self._new(self.value - other.value)
        else:
            return self._new(self.value - other)

    def __mul__(self, other):
        if isinstance(other, Cell):
            return self._new(self.value * other.value)
        else:
            return self._new(self.value * other)

    def __floordiv__(self, other):
        if isinstance(other, Cell):
            return self._new(self.value // other.value)
        else:
            return self._new(self.value // other)

    def __truediv__(self, other):
        if isinstance(other, Cell):
            return self._new(self.value / other.value)
        else:
            return self._new(self.value / other)

    def __mod__(self, other):
        if isinstance(other, Cell):
            return self._new(self.value % other.value)
        else:
            return self._new(self.value % other)

    def __pow__(self, other):
        if isinstance(other, Cell):
            return self._new(self.value ** other.value)
        else:
            return self._new(self.value ** other)

    def __radd__(self, other):
        if isinstance(other, Cell):
            return self._new(other.value + self.value)
        else:
            return self._new(other + self.value)

    def __rsub__(self, other):
        if isinstance(other, Cell):
            return self._new(other.value - self.value)
        else:
            return self._new(other - self.value)

    def __rmul__(self, other):
        if isinstance(other, Cell):
            return self._new(other.value * self.value)
        else:
            return self._new(other * self.value)

    def __rfloordiv__(self, other):
        if isinstance(other, Cell):
            return self._new(other.value // self.value)
        else:
            return self._new(other // self.value)

    def __rtruediv__(self, other):
        if isinstance(other, Cell):
            return self._new(other.value / self.value)
        else:
            return self._new(other / self.value)

    def __rmod__(self, other):
        if isinstance(other, Cell):
            return self._new(other.value % self.value)
        else:
            return self._new(other % self.value)

    def __rpow__(self, other):
        if isinstance(other, Cell):
            return self._new(other.value ** self.value)
        else:
            return self._new(other ** self.value)

    def __and__(self, other):
        if isinstance(other, Cell):
            return self._new(self.value & other.value)
        else:
            return self._new(self.value & other)

    def __xor__(self, other):
        if isinstance(other, Cell):
            return self._new(self.value ^ other.value)
        else:
            return self._new(self.value ^ other)

    def __or__(self, other):
        if isinstance(other, Cell):
            return self._new(self.value | other.value)
        else:
            return self._new(self.value | other)

    def __rand__(self, other):
        if isinstance(other, Cell):
            return self._new(other.value & self.value)
        else:
            return self._new(other & self.value)

    def __rxor__(self, other):
        if isinstance(other, Cell):
            return self._new(other.value ^ self.value)
        else:
            return self._new(other ^ self.value)

    def __ror__(self, other):
        if isinstance(other, Cell):
            return self._new(other.value | self.value)
        else:
            return self._new(other | self.value)

    def __iadd__(self, other):
        if isinstance(other, Cell):
            self.value += other.value
        else:
            self.value += other
        return self

    def __isub__(self, other):
        if isinstance(other, Cell):
            self.value -= other.value
        else:
            self.value -= other
        return self

    def __imul__(self, other):
        if isinstance(other, Cell):
            self.value *= other.value
        else:
            self.value *= other
        return self

    def __idiv__(self, other):
        self.column_type = "float"
        if isinstance(other, Cell):
            self.value /= other.value
        else:
            self.value /= other
        return self

    def __ifloordiv__(self, other):
        if isinstance(other, Cell):
            self.value //= other.value
        else:
            self.value //= other
        return self

    def __imod__(self, other):
        if isinstance(other, Cell):
            self.value %= other.value
        else:
            self.value %= other
        return self

    def __ipow__(self, other):
        if isinstance(other, Cell):
            self.value **= other.value
        else:
            self.value **= other
        return self

    def __pos__(self):
        return self._new(+self.value)

    def __neg__(self):
        return self._new(-self.value)

    def __abs__(self):
        return self._new(abs(self.value))

    def __invert__(self):
        return self._new(~self.value)

    def __int__(self):
        return int(self.value)

    def __float__(self):
        return float(self.value)

    def __oct__(self):
        return oct(self.value)

    def __hex__(self):
        return hex(self.value)

    def __round__(self, n=None):
        return self._new(round(self.value, n))

    def __ceil__(self):
        from math import ceil

        return self._new(ceil(self.value))

    def __floor__(self):
        from math import floor

        return self._new(floor(self.value))

    def __trunc__(self):
        from math import trunc

        return self._new(trunc(self.value))

    def __iter__(self):
        if isinstance(self.value, str):
            return self
        else:
            return NotImplemented

    def __next__(self):
        if isinstance(self.value, str):
            if self._i < len(self.value):
                val = self.value[self._i]
                self._i += 1
                return val
            else:
                self._i = 0
                raise StopIteration
        else:
            return NotImplemented

    def __len__(self):
        return len(self.value)

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"{self.value}, "
            f"{self.header}, "
            f"{self.row_num}, "
            f"{self.col_num})"
        )

    def __str__(self):
        if self.header in self._settings.dont_format:
            return str(self._value)
        else:
            return format_value(
                self._value, self.column_type, self._settings.datetime_format
            )

    def getquoted(self):
        if self.value is not None:
            return f"'{self.value}'"
        else:
            return "Null"

    def __hash__(self):
        return hash(repr(self.value))


try:
    # noinspection PyUnresolvedReferences
    from psycopg2.extensions import register_adapter

    def adapt_cell(cell):
        return cell

    register_adapter(Cell, adapt_cell)
except ImportError:
    pass
