"""Exercício 2: curry simples com functools.partial."""


def curry(func):
    """Devolva uma versão "curried" de ``func``.

    A versão devolvida acumula argumentos posicionais, em quantas
    chamadas você quiser, e só executa ``func`` quando já recebeu a
    quantidade de parâmetros obrigatórios dela. Use
    ``inspect.signature`` para contar os parâmetros posicionais sem
    valor padrão e ``functools.partial`` para acumular.

    >>> add3 = curry(lambda a, b, c: a + b + c)
    >>> add3(1)(2)(3)
    6
    >>> add3(1, 2)(3)
    6
    >>> add3(1, 2, 3)
    6
    """
    raise NotImplementedError
