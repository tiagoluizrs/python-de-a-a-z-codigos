"""Exercício 3: códigos de saída e erros sem traceback (o ``run`` que todo ``main`` precisa)."""
import sys


class UserError(Exception):
    """Erro esperado, causado por uma entrada do usuário: mostra uma linha, sem traceback."""


def run(main, argv=None, stderr=None, debug: bool = False) -> int:
    """Executa ``main(argv)`` e traduz o resultado em um código de saída, SEM nunca deixar uma exceção escapar:

    * ``main`` devolveu um ``int``: esse é o código; devolveu ``None``: ``0``;
    * ``UserError``: escreva ``erro: <mensagem>`` em ``stderr`` e devolva ``1``;
    * ``KeyboardInterrupt``: escreva uma linha vazia em ``stderr`` e devolva ``130``;
    * ``BrokenPipeError``: ``0`` e nada em ``stderr`` (o leitor do pipe fechou; não é erro seu);
    * ``SystemExit``: devolva o código dele (``None`` vira ``0``; um texto vira ``1`` e é escrito em ``stderr``);
    * qualquer outra ``Exception``: escreva ``erro interno: <ClasseDoErro>: <mensagem>`` em ``stderr`` (sem
      traceback) e devolva ``70``. Com ``debug=True``, escreva também o traceback completo
      (``traceback.format_exc()``) ANTES dessa linha.

    ``argv`` e ``stderr`` assumem ``sys.argv[1:]`` e ``sys.stderr`` quando ``None``."""
    raise NotImplementedError
