"""Gabarito do exercício 4."""
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation


@dataclass(frozen=True)
class Product:
    sku: str
    name: str
    price_cents: int
    tags: tuple
    in_stock: bool


def parse_price(value):
    if isinstance(value, bool) or value is None:
        raise ValueError(f"preço inválido: {value!r}")
    try:
        if isinstance(value, (int, float)):
            number = Decimal(str(value))
        elif isinstance(value, str):
            text = value.strip()
            if "," in text:
                text = text.replace(".", "").replace(",", ".")
            number = Decimal(text)
        else:
            raise ValueError
    except (InvalidOperation, ValueError):
        raise ValueError(f"preço inválido: {value!r}") from None
    if not number.is_finite():
        raise ValueError(f"preço inválido: {value!r}")
    if number < 0:
        raise ValueError("preço negativo")
    return int((number * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def parse_bool(value):
    if isinstance(value, bool):
        return value
    if value in (0, 1) and not isinstance(value, str):
        return bool(value)
    if isinstance(value, str):
        text = value.strip().lower()
        if text in ("s", "sim", "1", "true"):
            return True
        if text in ("n", "nao", "não", "0", "false"):
            return False
    raise ValueError(f"booleano inválido: {value!r}")


def adapt_product(raw):
    for field in ("codigo", "nome", "preco", "estoque"):
        if field not in raw:
            raise ValueError(f"campo ausente: {field}")
    name = str(raw["nome"]).strip()
    if not name:
        raise ValueError("nome vazio")
    tags = []
    for tag in (raw.get("etiquetas") or "").split(";"):
        tag = tag.strip().lower()
        if tag and tag not in tags:
            tags.append(tag)
    return Product(str(raw["codigo"]).strip().upper(), name, parse_price(raw["preco"]), tuple(tags), parse_bool(raw["estoque"]))


def adapt_many(rows):
    products, errors = [], []
    for i, row in enumerate(rows):
        try:
            products.append(adapt_product(row))
        except ValueError as error:
            errors.append((i, str(error)))
    return products, errors
