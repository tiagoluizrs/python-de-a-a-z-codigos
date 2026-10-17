"""Exercício 5: mesclar dicionários com regras de conflito."""
from collections.abc import Callable


def merge(base: dict, other: dict,
          on_conflict: Callable | None = None) -> dict:
    """Devolva um dict NOVO com a mesclagem de ``base`` e ``other``.

    Regras:

    - chaves só em um dos lados são copiadas;
    - se a chave existe nos dois e AMBOS os valores são dicts, mescle
      recursivamente (com a mesma regra de conflito);
    - nos demais conflitos, se ``on_conflict`` for dada, o valor é
      ``on_conflict(chave, valor_base, valor_other)``; senão, vence ``other``.

    Nenhuma das entradas pode ser modificada (nem os dicts internos).

    ``merge({"a": 1, "n": {"x": 1}}, {"a": 2, "n": {"y": 2}})``
    devolve ``{"a": 2, "n": {"x": 1, "y": 2}}``.
    """
    raise NotImplementedError
