"""Exercício 1: o tamanho 'de verdade' de um objeto."""


def deep_size(obj) -> int:
    """Some o ``sys.getsizeof`` do objeto e de TUDO que ele referencia.

    Regras:
    - percorra list, tuple, set, frozenset e dict (chaves E valores);
    - conte cada objeto uma única vez (use um conjunto com os ``id`` já vistos),
      pois o mesmo objeto pode aparecer em vários lugares;
    - não entre em loop infinito se houver referência circular.
    """
    raise NotImplementedError
