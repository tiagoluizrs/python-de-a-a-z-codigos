"""Gabarito do exercício 2."""
from dataclasses import dataclass, replace

ALLOWED = {"users": {"id", "name", "age", "city"}, "orders": {"id", "user_id", "total", "status"}}


@dataclass(frozen=True)
class Select:
    table: str
    columns: tuple = ("*",)
    conditions: tuple = ()
    params: tuple = ()
    order: tuple = ()
    max_rows: int | None = None
    skip: int = 0

    def __post_init__(self):
        if self.table not in ALLOWED:
            raise ValueError(f"tabela desconhecida: {self.table}")

    def _check(self, names):
        for name in names:
            if name != "*" and name not in ALLOWED[self.table]:
                raise ValueError(f"coluna desconhecida: {name}")

    def columns_(self, *names):
        self._check(names)
        return replace(self, columns=names)

    def where(self, column, op, value):
        self._check([column])
        if op not in ("=", "!=", "<", "<=", ">", ">="):
            raise ValueError(f"operador inválido: {op}")
        return replace(self, conditions=self.conditions + (f"{column} {op} ?",), params=self.params + (value,))

    def where_in(self, column, values):
        self._check([column])
        values = tuple(values)
        if not values:
            raise ValueError("lista vazia")
        marks = ", ".join("?" for _ in values)
        return replace(self, conditions=self.conditions + (f"{column} IN ({marks})",), params=self.params + values)

    def order_by(self, column, descending=False):
        self._check([column])
        return replace(self, order=self.order + (f"{column} {'DESC' if descending else 'ASC'}",))

    def limit(self, n):
        if int(n) < 0:
            raise ValueError("valor negativo")
        return replace(self, max_rows=int(n))

    def offset(self, n):
        if int(n) < 0:
            raise ValueError("valor negativo")
        return replace(self, skip=int(n))

    def build(self):
        sql = f"SELECT {', '.join(self.columns)} FROM {self.table}"
        if self.conditions:
            sql += " WHERE " + " AND ".join(self.conditions)
        if self.order:
            sql += " ORDER BY " + ", ".join(self.order)
        if self.max_rows is not None:
            sql += f" LIMIT {self.max_rows}"
        elif self.skip > 0:
            sql += " LIMIT -1"
        if self.skip > 0:
            sql += f" OFFSET {self.skip}"
        return sql, self.params
