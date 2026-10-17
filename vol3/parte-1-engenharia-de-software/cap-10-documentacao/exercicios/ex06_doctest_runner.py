"""Exercício 6: um mini doctest."""


def run_examples(docstring, namespace=None):
    """Executa os exemplos ``>>>`` de ``docstring`` e devolve a lista de
    FALHAS (vazia se tudo passou).

    Regras (um subconjunto do ``doctest``):

    * um exemplo começa em uma linha ``>>> código`` (com recuo qualquer);
      linhas ``... mais`` continuam o código; o ESPERADO são as linhas
      seguintes até uma linha em branco ou o próximo ``>>>``;
    * o código é executado em ``namespace`` (um dict; ``None`` cria um novo)
      que PERSISTE entre os exemplos;
    * se o código for uma EXPRESSÃO, a saída é ``repr(valor)`` (nada se o valor
      for ``None``) precedida de tudo o que foi impresso; se for instrução, só o
      que foi impresso (``contextlib.redirect_stdout``);
    * compare a saída (sem espaço nas pontas de cada linha) com o esperado;
    * exceção durante o exemplo: é falha, a menos que o esperado comece com
      ``Traceback (most recent call last):`` e a ÚLTIMA linha do esperado
      seja ``NomeDaExceção: mensagem`` igual a ``f"{type(e).__name__}: {e}"``.

    Cada falha é um dict ``{"source": código, "expected": str, "got": str}``."""
    raise NotImplementedError
