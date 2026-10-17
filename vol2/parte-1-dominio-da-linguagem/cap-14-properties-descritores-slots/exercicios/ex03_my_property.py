"""Exercício 3: reimplementar property em Python puro."""


class my_property:
    """Um ``property`` escrito à mão.

    * ``my_property(fget, fset=None, fdel=None, doc=None)``; a docstring vem
      de ``doc`` ou da docstring de ``fget``;
    * uso como decorador: ``@my_property`` e ``@x.setter`` / ``@x.deleter``
      (``setter`` e ``deleter`` devolvem um NOVO ``my_property``);
    * ``__get__``: pela classe (``obj is None``) devolve o próprio objeto;
      sem ``fget``, levanta ``AttributeError``;
    * ``__set__`` e ``__delete__``: sem ``fset``/``fdel``, levantam
      ``AttributeError``;
    * deve ser um descritor de DADOS (por isso define ``__set__``).
    """

    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        raise NotImplementedError
