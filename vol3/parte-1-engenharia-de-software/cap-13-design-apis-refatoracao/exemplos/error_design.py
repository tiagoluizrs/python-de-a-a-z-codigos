"""Erros como parte da API: hierarquia própria, mensagens úteis, três estilos."""
from dataclasses import dataclass


# 1) Uma hierarquia: quem usa a biblioteca captura a BASE
class ShopError(Exception):
    """Base de todos os erros desta biblioteca."""


class OutOfStock(ShopError):
    def __init__(self, sku, wanted, available):
        super().__init__(f"{sku}: pedidos {wanted}, disponíveis {available}")
        self.sku, self.wanted, self.available = sku, wanted, available


class UnknownProduct(ShopError, KeyError):
    """Também é KeyError: código que já tratava KeyError continua funcionando."""


STOCK = {"A1": 3}


def reserve(sku, qty):
    if sku not in STOCK:
        raise UnknownProduct(sku)
    if qty > STOCK[sku]:
        raise OutOfStock(sku, qty, STOCK[sku])
    STOCK[sku] -= qty
    return qty


for call in (("A1", 5), ("ZZ", 1), ("A1", 2)):
    try:
        print("reserve", call, "->", reserve(*call))
    except OutOfStock as error:
        print("  OutOfStock com dados estruturados:", error.sku, error.wanted, error.available, "|", error)
    except ShopError as error:
        print("  ShopError genérico:", type(error).__name__)

# 2) Valor de retorno especial (None, -1, False) esconde o erro
def find_bad(items, x):
    return items.index(x) if x in items else -1


print("-1 vira índice válido por engano:", ["a", "b", "c"][find_bad(["a", "b"], "z")])

# 3) Result: o erro é um valor (útil em pipelines; custo: cerimônia)
@dataclass(frozen=True)
class Ok:
    value: object


@dataclass(frozen=True)
class Err:
    error: str


def parse_port(text):
    if not text.isdigit():
        return Err(f"não numérico: {text!r}")
    port = int(text)
    return Ok(port) if 1 <= port <= 65535 else Err(f"fora da faixa: {port}")


for text in ("8080", "abc", "70000"):
    match parse_port(text):
        case Ok(value):
            print(f"  {text!r:>8} -> ok {value}")
        case Err(error):
            print(f"  {text!r:>8} -> erro: {error}")

print("regra: exceção para o inesperado/excepcional; Result ou valor explícito quando falhar é um resultado normal")
