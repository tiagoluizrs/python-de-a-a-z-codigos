"""Exercício 5: uma fábrica de classes com __slots__."""


def make_record(name, fields, weakref=False):
    """Crie e devolva uma classe chamada ``name`` com ``__slots__ = fields``.

    * ``cls(*valores)`` e ``cls(campo=valor)`` aceitam os campos na ordem
      de ``fields`` (posicional) ou por nome; faltar campo é ``TypeError``;
    * as instâncias NÃO têm ``__dict__``;
    * atribuir a um nome fora de ``fields`` levanta ``AttributeError``;
    * ``repr`` no formato ``Point(x=1, y=2)``;
    * ``==`` compara os campos (``NotImplemented`` para outros tipos);
    * com ``weakref=True``, as instâncias aceitam ``weakref.ref``
      (acrescente ``"__weakref__"`` aos slots).

    Dica: ``type(name, (), namespace)`` ou uma classe local definida dentro
    da função.
    """
    raise NotImplementedError
