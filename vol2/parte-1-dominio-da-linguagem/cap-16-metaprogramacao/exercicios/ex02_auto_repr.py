"""Exercício 2: gerar __repr__ pela assinatura do __init__."""


def auto_repr(cls):
    """Decorador de classe que cria ``__repr__`` baseado nos PARÂMETROS do
    ``__init__`` (use ``inspect.signature``).

    Para ``class P: def __init__(self, x, y=0)``, o repr é ``P(x=1, y=0)``,
    lendo ``self.x`` e ``self.y``. Parâmetros ``*args``/``**kwargs`` são
    ignorados. Se a classe já definir ``__repr__`` NO PRÓPRIO corpo
    (``"__repr__" in vars(cls)``), não o sobrescreva. Devolve a classe.
    """
    raise NotImplementedError
