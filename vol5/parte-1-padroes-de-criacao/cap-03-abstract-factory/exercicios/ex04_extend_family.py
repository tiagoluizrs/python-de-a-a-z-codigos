"""Exercício 4: o ponto fraco do padrão: acrescentar um PRODUTO a todas as famílias, com segurança."""


def extend_families(families: dict[str, dict], product: str, builders: dict) -> dict[str, dict]:
    """Devolve um NOVO dict de famílias em que cada uma ganha o produto ``product``, cuja função vem de ``builders[nome_da_familia]``.

    * NÃO altera ``families`` nem os dicts internos (devolva cópias);
    * ``product`` já existe em alguma família: ``ValueError(f"produto já existe: {product!r}")``;
    * faltam construtores para algumas famílias: ``ValueError(f"faltam construtores para: a, b")`` (nomes em ordem alfabética, separados por vírgula e espaço);
    * ``builders`` tem famílias que não existem: ``ValueError(f"famílias desconhecidas: x, y")`` (alfabético; esta verificação vem DEPOIS das outras duas);
    * o resultado mantém a ordem das famílias de ``families``."""
    raise NotImplementedError


def add_family(families: dict[str, dict], name: str, products: dict, *, like: str | None = None) -> dict[str, dict]:
    """Devolve um NOVO dict com a família ``name`` acrescentada ao fim (acrescentar família é o lado fácil do padrão).

    * ``name`` já existe: ``ValueError(f"família já existe: {name!r}")``;
    * os produtos da nova família precisam ter EXATAMENTE os mesmos nomes dos da família de referência (``like``, ou a primeira de ``families`` se
      ``None``); diferenças: ``ValueError(f"produtos incompatíveis: faltam a, b; sobram c")`` (omita a parte vazia: só ``faltam ...`` ou só ``sobram ...``;
      os nomes em ordem alfabética); ``like`` desconhecido: ``KeyError(like)``;
    * ``families`` vazio e ``like`` ``None``: aceita ``products`` sem verificar."""
    raise NotImplementedError
