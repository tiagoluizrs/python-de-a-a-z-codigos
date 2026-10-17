"""Repository (Capítulo 7 do Volume 3) sobre SQLite, com consultas dinâmicas SEGURAS (Capítulo 8 do Volume 3)."""
import sqlite3
from dataclasses import dataclass


@dataclass(frozen=True)
class Product:
    id: int
    name: str
    price: float
    category: str | None


ORDERABLE = {"name": "name", "price": "price", "id": "id"}          # lista de permissão para NOMES de coluna


def _like_escape(text):
    return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


class ProductRepository:
    def __init__(self, conn):
        self.conn = conn
        conn.row_factory = sqlite3.Row
        conn.execute("CREATE TABLE IF NOT EXISTS product (id INTEGER PRIMARY KEY, name TEXT NOT NULL, price REAL NOT NULL, category TEXT)")

    @staticmethod
    def _to_product(row):
        return Product(**dict(row))

    def add(self, name, price, category=None):
        row = self.conn.execute("INSERT INTO product (name, price, category) VALUES (?, ?, ?) RETURNING *", (name, price, category)).fetchone()
        self.conn.commit()
        return self._to_product(row)

    def search(self, *, name_contains=None, max_price=None, order_by="name", descending=False):
        if order_by not in ORDERABLE:
            raise ValueError(f"order_by inválido: {order_by!r}")      # nomes de coluna NÃO podem ser parâmetros
        where, params = [], []
        if name_contains:
            where.append("name LIKE ? ESCAPE '\\'")
            params.append(f"%{_like_escape(name_contains)}%")
        if max_price is not None:
            where.append("price <= ?")
            params.append(max_price)
        sql = "SELECT * FROM product"
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += f" ORDER BY {ORDERABLE[order_by]} {'DESC' if descending else 'ASC'}"
        return [self._to_product(r) for r in self.conn.execute(sql, params)]


if __name__ == "__main__":
    repo = ProductRepository(sqlite3.connect(":memory:"))
    for name, price, category in [("caneta azul", 2.5, "papelaria"), ("caneta_preta", 3.0, "papelaria"), ("100% algodão", 40.0, "roupas")]:
        repo.add(name, price, category)
    print("busca 'caneta'      :", [p.name for p in repo.search(name_contains="caneta")])
    print("busca '%' literal   :", [p.name for p in repo.search(name_contains="%")], "(o % foi escapado, não é curinga)")
    print("busca '_' literal   :", [p.name for p in repo.search(name_contains="_")])
    print("barato, mais caro 1º:", [p.name for p in repo.search(max_price=10, order_by="price", descending=True)])
    try:
        repo.search(order_by="price; DROP TABLE product")
    except ValueError as error:
        print("injeção no ORDER BY recusada:", error)
    print("injeção no valor é inofensiva:", repo.search(name_contains="'; DROP TABLE product; --"), "| tabela intacta:", len(repo.search()), "produtos")
