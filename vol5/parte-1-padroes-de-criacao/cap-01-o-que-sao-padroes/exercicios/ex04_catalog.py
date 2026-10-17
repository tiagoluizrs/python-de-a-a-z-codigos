"""Exercício 4: consultas sobre o catálogo de padrões (uma lista de dicts, como a de ``exemplos/catalogo.py``)."""


def by_family(catalog: list[dict]) -> dict[str, list[str]]:
    """``{família: [nomes]}``, com as famílias e os nomes na ORDEM em que aparecem em ``catalog``."""
    raise NotImplementedError


def verdict_counts(catalog: list[dict]) -> dict[str, int]:
    """``{veredito: quantidade}``, com as chaves em ordem alfabética."""
    raise NotImplementedError


def embedded(catalog: list[dict]) -> list[str]:
    """Os nomes cujo ``verdict`` é ``"embutido"``, em ordem alfabética."""
    raise NotImplementedError


def chapters_of(catalog: list[dict], *names: str) -> list[int]:
    """Os capítulos dos padrões citados, NA ORDEM dos nomes recebidos (sem diferenciar maiúsculas de minúsculas). Nome desconhecido:
    ``KeyError(nome)``."""
    raise NotImplementedError


def missing_chapters(catalog: list[dict], extras: list[dict], first: int, last: int) -> list[int]:
    """Os capítulos de ``first`` a ``last`` (inclusive) que NÃO aparecem em nenhum item de ``catalog`` nem de ``extras``, em ordem crescente."""
    raise NotImplementedError


def python_share(catalog: list[dict]) -> float:
    """A fração (``round(..., 2)``) de padrões com veredito ``"embutido"`` ou ``"simplificado"``. Catálogo vazio: ``ValueError``."""
    raise NotImplementedError
