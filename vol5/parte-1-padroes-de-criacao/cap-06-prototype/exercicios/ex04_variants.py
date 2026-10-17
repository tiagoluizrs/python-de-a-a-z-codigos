"""Exercício 4: variantes de um objeto com ``copy.replace`` (3.13+) e cópias de estruturas simples mais rápidas que ``deepcopy``."""


def variant(obj, **changes):
    """Uma cópia de ``obj`` com os campos trocados, pelo protocolo ``__replace__`` (``copy.replace``). Funciona com dataclasses, ``namedtuple``,
    ``datetime``... Um campo que não existe: o ``TypeError`` que ``copy.replace`` levanta (não o esconda). O original NUNCA é alterado."""
    raise NotImplementedError


def variants(base, field: str, values) -> list:
    """Uma variante de ``base`` para CADA valor de ``values``, trocando só o campo ``field`` (``[variant(base, **{field: v}) for v in values]``), na ordem."""
    raise NotImplementedError


def copy_matrix(m: list[list]) -> list[list]:
    """Cópia independente de uma lista de listas de valores ATÔMICOS (números, textos...), sem usar ``deepcopy`` (``[row[:] for row in m]`` ou
    equivalente). Linhas de tamanhos diferentes são aceitas; uma linha que não seja ``list``: ``TypeError("linha inválida: ...")`` (com o ``repr`` da linha)."""
    raise NotImplementedError


def copy_json(data):
    """Cópia independente de dados no formato JSON (``dict`` com chaves de texto, ``list``, ``str``, ``int``, ``float``, ``bool``, ``None``), por RECURSÃO
    (não use ``deepcopy`` nem ``json``). Um tipo que não é JSON (``set``, ``tuple``, objetos...): ``TypeError(f"tipo não suportado: {tipo}")``
    com o ``__name__`` do tipo; chave que não é texto: ``TypeError("chave inválida: ...")``."""
    raise NotImplementedError
