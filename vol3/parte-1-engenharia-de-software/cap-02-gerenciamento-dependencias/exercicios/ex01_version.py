"""Exercício 1: ordenar versões (um subconjunto da PEP 440)."""


def version_key(text):
    """Chave de ordenação para versões no formato
    ``N(.N)*[(a|b|rc)N][.postN][.devN]`` (sem epoch nem hífens).

    Regras de ordem (as da PEP 440): ``1.0.dev0 < 1.0a1 < 1.0b2 < 1.0rc1 <
    1.0 < 1.0.post1``; ``1.0 == 1.0.0`` (zeros finais não contam); e
    ``1.0.post1.dev0`` vem ANTES de ``1.0.post1``.

    Devolve algo comparável com ``<`` (use uma tupla). Texto fora do
    formato levanta ``ValueError``."""
    raise NotImplementedError


def newest(versions, allow_prerelease=False):
    """A maior versão de ``versions`` (lista de textos), ignorando
    pré-lançamentos (``a``, ``b``, ``rc``) e versões ``dev`` a menos que
    ``allow_prerelease`` seja ``True`` ou só existam elas. Lista vazia levanta
    ``ValueError``. Devolve o texto original."""
    raise NotImplementedError
