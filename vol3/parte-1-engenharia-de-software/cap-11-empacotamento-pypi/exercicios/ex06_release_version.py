"""Exercício 6: calcular a próxima versão (um subconjunto da PEP 440)."""


def bump(version, part):
    """``part`` em ``"major"``, ``"minor"``, ``"patch"``: ``bump("1.4.2", "minor")``
    -> ``"1.5.0"``; ``"major"`` -> ``"2.0.0"``; ``"patch"`` -> ``"1.4.3"``. Aceita
    só versões FINAIS ``N.N.N``; pré-lançamentos, ``.dev``, ``.post`` ou formato
    inválido levantam ``ValueError`` (``part`` inválida também)."""
    raise NotImplementedError


def to_prerelease(version, kind):
    """Primeiro pré-lançamento ou o seguinte. ``kind`` em ``"a"``, ``"b"``, ``"rc"``.

    * versão final ``"1.5.0"`` + ``"rc"`` -> ``"1.5.0rc1"``;
    * já pré-lançamento do MESMO tipo (``"1.5.0rc1"`` + ``"rc"``) -> ``"1.5.0rc2"``;
    * pré-lançamento de tipo ANTERIOR avança de tipo e reinicia em 1
      (``"1.5.0a3"`` + ``"b"`` -> ``"1.5.0b1"``; ordem ``a < b < rc``);
    * tipo ANTERIOR ao atual (``"1.5.0rc1"`` + ``"a"``) levanta ``ValueError``;
    * formato inválido levanta ``ValueError``."""
    raise NotImplementedError


def finalize(version):
    """Remove o pré-lançamento: ``"1.5.0rc2"`` -> ``"1.5.0"``; versão já final
    fica como está; inválida levanta ``ValueError``."""
    raise NotImplementedError
