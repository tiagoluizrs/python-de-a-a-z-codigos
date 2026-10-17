"""Exercício 5: composição de funções com o operador |."""


class Step:
    """Envolve uma função e permite compor com ``|`` (estilo shell).

    * ``Step(f)(x)`` chama ``f(x)``;
    * ``Step(f) | Step(g)`` (ou ``Step(f) | g`` com ``g`` uma função comum)
      devolve um ``Step`` que aplica ``f`` e depois ``g``;
    * ``g | Step(f)`` (função comum à esquerda) também funciona
      (``__ror__``);
    * ``valor >> step`` aplica o passo ao valor (``__rrshift__``), por
      exemplo ``"  Ola " >> (Step(str.strip) | str.lower)`` dá ``"ola"``;
    * ``repr`` no formato ``Step(strip | lower)`` usando os ``__name__``;
    * tipos que não são callables devem levantar ``TypeError``
      (devolva ``NotImplemented``).
    """

    def __init__(self, func, name=None):
        raise NotImplementedError
