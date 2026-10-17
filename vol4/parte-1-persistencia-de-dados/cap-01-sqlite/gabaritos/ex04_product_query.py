"""Gabarito do exercício 4."""
_ORDER = {"id", "name", "price"}


def _escape(text):
    return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def build_product_query(name_contains=None, min_price=None, max_price=None, category=None,
                        order_by="name", descending=False, limit=50, offset=0):
    if order_by not in _ORDER:
        raise ValueError(f"order_by inválido: {order_by!r}")
    if not 1 <= limit <= 200 or offset < 0:
        raise ValueError("limit entre 1 e 200 e offset >= 0")
    where, params = [], []
    if name_contains is not None:
        where.append("name LIKE ? ESCAPE '\\'")
        params.append(f"%{_escape(name_contains)}%")
    if min_price is not None:
        where.append("price >= ?")
        params.append(min_price)
    if max_price is not None:
        where.append("price <= ?")
        params.append(max_price)
    if category is not None:
        where.append("category = ?")
        params.append(category)
    sql = "SELECT id, name, price, category FROM product"
    if where:
        sql += " WHERE " + " AND ".join(where)
    direction = "DESC" if descending else "ASC"
    sql += f" ORDER BY {order_by} {direction}, id ASC LIMIT ? OFFSET ?"
    params += [limit, offset]
    return sql, params
