"""Exercício 5: testes de caracterização (golden master)."""


def capture(func, inputs):
    """Para cada ``args`` (uma TUPLA) em ``inputs``, chama ``func(*args)`` e guarda em
    um dict ``{args: resultado}``. Se levantar exceção, guarda o texto
    ``"<NomeDaExceção>: <mensagem>"`` no lugar. A ordem das chaves é a de ``inputs``."""
    raise NotImplementedError


def diff_masters(old, new):
    """Compara dois dicts de ``capture``. Devolve ``{"changed": {args: (antigo, novo)},
    "missing": [args em old e não em new], "extra": [args em new e não em old]}``
    (``changed`` só com os que existem nos dois e diferem; listas na ordem de ``old``/``new``)."""
    raise NotImplementedError


def refactor_is_safe(old_func, new_func, inputs):
    """``(True, {})`` se ``old_func`` e ``new_func`` se comportam IGUAL em todas as
    ``inputs`` (mesmos resultados e mesmas exceções, tipo e mensagem); senão
    ``(False, diferenças)`` onde ``diferenças`` é o ``changed`` de ``diff_masters``."""
    raise NotImplementedError
