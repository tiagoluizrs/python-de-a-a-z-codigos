"""Exercício 3: a biblioteca padrão como fábrica abstrata: ``posixpath`` e ``ntpath`` são duas FAMÍLIAS com os mesmos nomes."""
import ntpath
import posixpath


def family_for(system: str):
    """O módulo da família: ``"posix"`` -> ``posixpath``; ``"nt"`` -> ``ntpath`` (sem diferenciar maiúsculas de minúsculas).
    Outro valor: ``ValueError(f"sistema desconhecido: {system!r}")``."""
    raise NotImplementedError


def portable_join(system: str, *parts: str) -> str:
    """``join`` na família do sistema. Sem partes: ``ValueError("sem partes")``."""
    raise NotImplementedError


def describe(system: str) -> dict:
    """``{"sep": ..., "case_sensitive": ..., "has_drive": ...}``: o separador da família; se ela diferencia maiúsculas de minúsculas
    (``normcase("A") == "A"``); e se ela reconhece letras de unidade (``splitdrive("C:/x")[0] == "C:"``)."""
    raise NotImplementedError


def same_file(system: str, a: str, b: str) -> bool:
    """Se ``a`` e ``b`` são o MESMO caminho para o sistema, depois de ``normpath`` e ``normcase`` (no ``nt``, ``"C:/A/../B"`` e ``"c:\\\\b"`` são o mesmo)."""
    raise NotImplementedError
