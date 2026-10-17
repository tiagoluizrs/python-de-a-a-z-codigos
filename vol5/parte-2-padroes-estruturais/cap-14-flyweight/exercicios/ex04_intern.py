"""Exercício 4: *interning* de valores repetidos (textos e tuplas) que chegam de fora (arquivos, JSON, bancos) e o Python NÃO compartilha sozinho."""


class Interner:
    """Um pool de valores iguais.

    * ``intern(value)``: devolve o PRIMEIRO objeto visto que seja ``==`` a ``value`` (e do mesmo tipo!: ``1`` e ``True`` e ``1.0`` são ``==``, mas NÃO são o
      mesmo valor aqui: a chave do pool é ``(type(value), value)``); valores NÃO hashable (``list``, ``dict``): ``TypeError(f"valor não hashable: {tipo}")``
      com o ``__name__`` do tipo;
    * ``stats()``: ``{"calls": n, "unique": n}`` (chamadas a ``intern`` e valores distintos guardados);
    * ``clear()``: esvazia o pool e zera as estatísticas;
    * ``__len__``: quantos valores distintos há."""

    def __init__(self):
        raise NotImplementedError

    def intern(self, value):
        raise NotImplementedError

    def stats(self) -> dict:
        raise NotImplementedError

    def clear(self) -> None:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError


def dedupe_records(rows: list[dict], interner: Interner | None = None) -> list[dict]:
    """Devolve uma NOVA lista de NOVOS dicts em que cada valor ``str`` (e tupla de ``str``) passa pelo ``interner`` (um novo se ``None``; cuidado: um ``Interner`` VAZIO é falso por causa do ``__len__``, então compare com ``None`` em vez de usar ``or``), de modo que textos iguais
    sejam o MESMO objeto em todos os registros; as chaves também são internadas; os demais valores (números, ``None``, listas...) ficam como estão. Os dicts
    originais NÃO são alterados."""
    raise NotImplementedError


def distinct_objects(rows: list[dict], key: str) -> int:
    """Quantos objetos DISTINTOS (por ``id``) aparecem como valor da chave ``key`` nas linhas que a têm. Sem nenhuma linha com a chave: ``0``."""
    raise NotImplementedError


def duplication_report(rows: list[dict]) -> dict[str, tuple[int, int]]:
    """Para cada chave que aparece em ``rows``, ``(valores_str, textos_distintos_por_valor)``: quantos valores ``str`` há ao todo e quantos são DIFERENTES por ``==``
    (não por identidade). Só chaves com pelo menos um valor ``str``; o dict sai com as chaves em ordem alfabética."""
    raise NotImplementedError
