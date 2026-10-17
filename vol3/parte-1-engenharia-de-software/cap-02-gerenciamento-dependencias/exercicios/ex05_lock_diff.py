"""Exercício 5: comparar dois arquivos de trava."""


def locked_versions(lock_text):
    """Lê o texto de um ``uv.lock`` (TOML com uma lista ``[[package]]``, cada
    item com ``name`` e ``version``) e devolve ``{nome: versão}``. Use
    ``tomllib``. Sem pacotes, ``{}``."""
    raise NotImplementedError


def diff_locks(old_text, new_text):
    """Compara duas travas e devolve um dict com:

    * ``"added"``: ``{nome: versão}`` dos que só existem na nova;
    * ``"removed"``: ``{nome: versão}`` dos que só existiam na antiga;
    * ``"upgraded"``: ``{nome: (antiga, nova)}`` com versão MAIOR;
    * ``"downgraded"``: ``{nome: (antiga, nova)}`` com versão MENOR.

    Compare versões numericamente (``1.10 > 1.9``): versões só com números e
    pontos nos testes. Iguais não aparecem."""
    raise NotImplementedError


def summarize(diff):
    """Resumo de uma linha: ``"2 adicionados, 1 removido, 3 atualizados,
    0 rebaixados"`` (singular quando for 1: ``adicionado``, ``removido``,
    ``atualizado``, ``rebaixado``; plural com ``s``; ``0`` plural)."""
    raise NotImplementedError
