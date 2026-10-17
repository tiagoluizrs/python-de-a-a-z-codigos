"""Exercício 4: um descritor que calcula uma vez e se cacheia."""


class lazy:
    """Como ``functools.cached_property``, escrito por você.

    * usado como decorador de um método sem argumentos além de ``self``;
    * no PRIMEIRO acesso calcula e guarda o valor em ``obj.__dict__`` sob o
      mesmo nome (o descritor NÃO define ``__set__``, para o valor guardado
      vencer nas leituras seguintes);
    * acesso pela classe devolve o próprio descritor;
    * ``del obj.nome`` (remover do ``__dict__``) faz recalcular;
    * a docstring do método é preservada em ``lazy.__doc__``.
    """

    def __init__(self, func):
        raise NotImplementedError
