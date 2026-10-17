"""Exercício 4: o Borg (monostate): várias instâncias, UM estado compartilhado por classe."""


class Borg:
    """Todas as instâncias de uma mesma classe compartilham o MESMO ``__dict__``; instâncias continuam distintas (``Borg() is not Borg()``).

    * cada SUBCLASSE tem o seu próprio estado (``Config1`` e ``Config2`` não se misturam), criado ao definir a subclasse (``__init_subclass__``);
      a própria ``Borg`` também tem o seu;
    * ``reset_state()`` (``classmethod``) apaga o estado da classe (``clear()``), valendo para todas as instâncias já criadas;
    * ``__eq__``: duas instâncias são iguais se são da mesma classe (o estado é o mesmo por definição) e ``hash`` consistente
      (``hash(type(self))``)."""

    def __init__(self):
        raise NotImplementedError

    @classmethod
    def reset_state(cls):
        raise NotImplementedError
