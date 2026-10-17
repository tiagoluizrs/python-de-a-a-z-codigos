"""Exercício 4: um dict de chaves minúsculas que não vaza por nenhum método."""


class LowerDict:
    """Mapeamento cujas chaves ``str`` são SEMPRE minúsculas.

    Implemente com ``collections.UserDict`` (ou ``MutableMapping``) para que
    TODOS os caminhos passem pela normalização:

    * ``LowerDict(HOST=1)`` e ``LowerDict({"A": 1}, B=2)``;
    * ``d["NAME"] = 1`` e ``d["name"]`` / ``d["Name"]`` leem o mesmo item;
    * ``update``, ``setdefault``, ``in``, ``get``, ``pop`` e ``del``;
    * ``list(d)`` devolve as chaves em minúsculas;
    * chaves que não são ``str`` ficam como estão;
    * a classe deve ser ``isinstance`` de ``collections.abc.MutableMapping``
      e NÃO pode ser subclasse de ``dict``.
    """
