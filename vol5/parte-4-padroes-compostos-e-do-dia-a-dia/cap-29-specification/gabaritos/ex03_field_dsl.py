"""Gabarito do exercício 3."""
import operator

COLUMNS = {"id", "name", "age", "country", "vip", "banned"}
OPS = {"==": operator.eq, "!=": operator.ne, "<": operator.lt, "<=": operator.le, ">": operator.gt, ">=": operator.ge}
SQL_OPS = {"==": "=", "!=": "<>"}


class Spec3:
    def __and__(self, other):
        return And(self, other)

    def __or__(self, other):
        return Or(self, other)

    def __invert__(self):
        return Not(self)

    def __call__(self, row):
        return self.evaluate(row) is True


class Cmp(Spec3):
    def __init__(self, column, op, value):
        if value is None:
            raise ValueError("use is_null() para comparar com NULL")
        self.column, self.op, self.value = column, op, value

    def evaluate(self, row):
        actual = row.get(self.column)
        return None if actual is None else OPS[self.op](actual, self.value)

    def to_sql(self):
        return f"{self.column} {SQL_OPS.get(self.op, self.op)} ?", (self.value,)

    def __repr__(self):
        return f"{self.column} {self.op} {self.value!r}"


class IsNull(Spec3):
    def __init__(self, column):
        self.column = column

    def evaluate(self, row):
        return row.get(self.column) is None

    def to_sql(self):
        return f"{self.column} IS NULL", ()

    def __repr__(self):
        return f"{self.column} é nulo"


class And(Spec3):
    def __init__(self, left, right):
        self.left, self.right = left, right

    def evaluate(self, row):
        a, b = self.left.evaluate(row), self.right.evaluate(row)
        if a is False or b is False:
            return False
        return None if a is None or b is None else True

    def to_sql(self):
        (ls, lp), (rs, rp) = self.left.to_sql(), self.right.to_sql()
        return f"({ls} AND {rs})", lp + rp

    def __repr__(self):
        return f"({self.left!r} e {self.right!r})"


class Or(Spec3):
    def __init__(self, left, right):
        self.left, self.right = left, right

    def evaluate(self, row):
        a, b = self.left.evaluate(row), self.right.evaluate(row)
        if a is True or b is True:
            return True
        return None if a is None or b is None else False

    def to_sql(self):
        (ls, lp), (rs, rp) = self.left.to_sql(), self.right.to_sql()
        return f"({ls} OR {rs})", lp + rp

    def __repr__(self):
        return f"({self.left!r} ou {self.right!r})"


class Not(Spec3):
    def __init__(self, inner):
        self.inner = inner

    def evaluate(self, row):
        value = self.inner.evaluate(row)
        return None if value is None else not value

    def to_sql(self):
        sql, params = self.inner.to_sql()
        return f"(NOT {sql})", params

    def __repr__(self):
        return f"não {self.inner!r}"


class Field:
    def __init__(self, name):
        if name not in COLUMNS:
            raise AttributeError(f"coluna desconhecida: {name}")
        self.name = name

    def __eq__(self, value):
        return Cmp(self.name, "==", value)

    def __ne__(self, value):
        return Cmp(self.name, "!=", value)

    def __lt__(self, value):
        return Cmp(self.name, "<", value)

    def __le__(self, value):
        return Cmp(self.name, "<=", value)

    def __gt__(self, value):
        return Cmp(self.name, ">", value)

    def __ge__(self, value):
        return Cmp(self.name, ">=", value)

    __hash__ = None

    def isin(self, values):
        options = [Cmp(self.name, "==", v) for v in values]
        if not options:
            raise ValueError("isin precisa de pelo menos um valor")
        result = options[0]
        for other in options[1:]:
            result = Or(result, other)
        return result

    def between(self, low, high):
        return (self >= low) & (self <= high)

    def is_null(self):
        return IsNull(self.name)

    def is_not_null(self):
        return ~self.is_null()


class _F:
    def __getattr__(self, name):
        return Field(name)


F = _F()
