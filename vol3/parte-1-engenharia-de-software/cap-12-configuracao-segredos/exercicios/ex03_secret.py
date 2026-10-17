"""Exercício 3: um tipo para valores sensíveis."""


class Secret:
    """Guarda um texto sensível.

    * ``Secret("abc")``; ``reveal()`` devolve o valor;
    * ``repr`` e ``str`` mostram ``"Secret('**********')"`` (sempre 10 asteriscos,
      sem revelar o tamanho);
    * ``==`` só com outro ``Secret`` e em TEMPO CONSTANTE (``hmac.compare_digest``);
      com outro tipo, ``NotImplemented``;
    * NÃO é hasheável (``hash()`` levanta ``TypeError``);
    * ``pickle.dumps`` e ``copy.copy`` levantam ``TypeError`` (``__reduce__``);
    * ``bool(Secret(""))`` é ``False``, ``len`` não existe;
    * o valor não pode ser lido por ``vars()``/``__dict__`` (use ``__slots__``).
    """

    def __init__(self, value):
        raise NotImplementedError

    def reveal(self):
        raise NotImplementedError
