"""Exercício 5: quando o objeto morre, pelo contador ou pelo gc?"""
from collections.abc import Callable


def release_mode(factory: Callable[[], object]) -> str:
    """Descubra como o objeto criado por ``factory`` é liberado.

    Devolva:
    - ``"refcount"`` se ele morre assim que o último nome é solto;
    - ``"gc"`` se só morre após ``gc.collect()``;
    - ``"never"`` se continua vivo mesmo depois do ``gc.collect()``.

    Dicas: guarde apenas uma ``weakref.ref`` do objeto, desligue o coletor
    automático com ``gc.disable()`` durante o teste (e religue no ``finally``),
    solte o nome forte e consulte a referência fraca.
    ``factory`` deve devolver um objeto que aceite weakref.
    """
    raise NotImplementedError
