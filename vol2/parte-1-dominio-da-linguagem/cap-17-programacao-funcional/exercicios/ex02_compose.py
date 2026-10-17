"""Exercício 2: composição e currying."""


def compose(*funcs):
    """``compose(f, g, h)(x) == f(g(h(x)))``. Sem funções, devolve uma função
    identidade. O primeiro a executar aceita QUALQUER quantidade de argumentos;
    os demais recebem um só."""
    raise NotImplementedError


def pipe(value, *funcs):
    """``pipe(x, f, g) == g(f(x))``. Sem funções, devolve ``value``."""
    raise NotImplementedError


def curry(func):
    """Currying automático pela assinatura (``inspect.signature``).

    ``curry(lambda a, b, c: a + b + c)`` aceita ``(1)(2)(3)``, ``(1, 2)(3)``,
    ``(1)(2, 3)`` e ``(1, 2, 3)``: enquanto faltarem argumentos obrigatórios,
    devolve uma nova função; quando completar, chama ``func``. Considere só
    parâmetros posicionais obrigatórios (sem padrão).
    """
    raise NotImplementedError
