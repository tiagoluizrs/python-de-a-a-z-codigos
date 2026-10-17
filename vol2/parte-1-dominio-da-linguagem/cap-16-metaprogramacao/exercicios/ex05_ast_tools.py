"""Exercício 5: análise estática com ast."""


def called_names(source):
    """Devolve a lista ORDENADA e sem repetição dos nomes chamados em ``source``
    (texto de código): ``f(x)`` conta ``"f"``; ``obj.method(y)`` conta
    ``"method"``. Chamadas aninhadas (``f(g(x))``) contam as duas.
    """
    raise NotImplementedError


def has_unsafe_calls(source, forbidden=("eval", "exec", "compile", "__import__")):
    """``True`` se ``source`` CHAMAR (como nome simples) algum nome proibido.
    Apenas mencionar (``x = eval``) NÃO conta; chamar (``eval(...)``) conta."""
    raise NotImplementedError


def constants_to_upper(source):
    """Devolve o texto de ``source`` com todas as constantes ``str`` passadas
    para MAIÚSCULAS (use ``ast.NodeTransformer`` e ``ast.unparse``)."""
    raise NotImplementedError
