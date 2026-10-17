"""Exercício 2: o ``.dockerignore`` (o contexto de build é enviado inteiro ao Docker: o que sobra custa tempo e segredo)."""


def is_ignored(path: str, patterns: list[str]) -> bool:
    """Diz se ``path`` (relativo à raiz do contexto, com ``/``, sem ``./`` no começo; ex.: ``"src/app/main.py"``) é ignorado.

    Regras (as do ``.dockerignore``):

    * linhas vazias e comentários (``#``) são ignorados; espaços nas pontas também;
    * ``*`` casa qualquer sequência SEM ``/``; ``?`` casa um caractere qualquer SEM ``/``; ``**`` casa qualquer sequência
      INCLUINDO ``/`` (inclusive zero diretórios: ``**/*.pyc`` casa ``a.pyc`` e ``x/y/a.pyc``);
    * o padrão é ancorado na raiz: ``node_modules`` casa só o ``node_modules`` da raiz (e tudo dentro dele); para casar em
      qualquer nível, use ``**/node_modules``. Um padrão que casa um DIRETÓRIO ignora tudo dentro dele;
    * uma barra no começo (``/build``) e uma barra no fim (``build/``) são ignoradas (o padrão é o mesmo que ``build``);
    * ``!padrao`` é uma EXCEÇÃO: reinclui o que casar; vale a ÚLTIMA regra que casa (na ordem do arquivo);
    * sem nenhuma regra que case, o caminho NÃO é ignorado."""
    raise NotImplementedError


def build_context(paths: list[str], patterns: list[str]) -> list[str]:
    """Os caminhos que SERÃO enviados ao Docker (os não ignorados), na ordem recebida."""
    raise NotImplementedError
