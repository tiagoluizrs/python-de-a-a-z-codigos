"""Exercício 6: juntar vários fluxos assíncronos."""


async def merge_streams(*streams):
    """Gerador assíncrono que consome VÁRIOS iteradores assíncronos ao mesmo tempo e
    entrega cada item assim que ele chega (de qualquer fluxo). Termina quando
    todos acabarem.

    * cada fluxo é consumido por uma tarefa que põe os itens em uma fila;
    * se um fluxo levantar uma exceção, as outras tarefas são canceladas e a
      exceção se propaga (como ``ExceptionGroup`` ou direta: aceite as duas no
      teste, mas NÃO engula);
    * se o consumidor parar antes (``break``/``aclose``), todas as tarefas devem
      ser CANCELADAS e esperadas (use ``try/finally``);
    * sem ``streams`` termina imediatamente."""
    raise NotImplementedError
    yield  # pragma: no cover  (marca a função como gerador assíncrono)
