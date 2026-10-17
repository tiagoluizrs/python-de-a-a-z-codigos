"""Exercício 4: adaptar DADOS: o formato legado (nomes em português, textos para tudo) para o modelo do nosso código."""
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal


@dataclass(frozen=True)
class Product:
    sku: str
    name: str
    price_cents: int
    tags: tuple
    in_stock: bool


def parse_price(value) -> int:
    """Converte para CENTAVOS (``int``), arredondando metade para cima (``ROUND_HALF_UP``). Aceita ``int``/``float`` (use ``Decimal(str(valor))``, não ``Decimal(float)``) e
    textos no formato brasileiro (``"12,50"``, ``"1.234,5"``: o ponto separa milhares, a vírgula separa os decimais) ou simples (``"12.5"``). Negativo:
    ``ValueError("preço negativo")``; qualquer outra coisa (texto não numérico, ``None``, ``bool``): ``ValueError(f"preço inválido: {valor!r}")``."""
    raise NotImplementedError


def parse_bool(value) -> bool:
    """``True``/``False`` passam. Textos (sem diferenciar maiúsculas, sem espaços nas pontas): ``"s"``, ``"sim"``, ``"1"``, ``"true"`` -> ``True``;
    ``"n"``, ``"nao"``, ``"não"``, ``"0"``, ``"false"`` -> ``False``; ``1`` e ``0`` (inteiros) também. Outro valor: ``ValueError(f"booleano inválido: {valor!r}")``."""
    raise NotImplementedError


def adapt_product(raw: dict) -> Product:
    """Do formato legado ``{"codigo", "nome", "preco", "etiquetas", "estoque"}`` para ``Product``:

    * ``sku`` = ``codigo`` sem espaços nas pontas e em MAIÚSCULAS; ``name`` = ``nome`` sem espaços nas pontas (vazio: ``ValueError("nome vazio")``);
    * ``price_cents`` = ``parse_price(preco)``; ``in_stock`` = ``parse_bool(estoque)``;
    * ``tags`` = ``etiquetas`` (texto separado por ``;``) viradas tupla: sem espaços nas pontas, sem itens vazios, sem repetições (mantém a ordem da
      primeira aparição), em minúsculas; ``etiquetas`` ausente ou ``None`` vale tupla vazia;
    * campo obrigatório ausente (todos menos ``etiquetas``): ``ValueError(f"campo ausente: {nome}")`` (na ordem ``codigo``, ``nome``, ``preco``, ``estoque``);
    * campos desconhecidos são ignorados."""
    raise NotImplementedError


def adapt_many(rows: list[dict]) -> tuple[list[Product], list[tuple[int, str]]]:
    """Adapta cada linha; uma linha que falha com ``ValueError`` NÃO interrompe as outras. Devolve ``(produtos, erros)``; ``erros`` é a lista de
    ``(índice, mensagem)`` (índice a partir de 0, na ordem das linhas)."""
    raise NotImplementedError
