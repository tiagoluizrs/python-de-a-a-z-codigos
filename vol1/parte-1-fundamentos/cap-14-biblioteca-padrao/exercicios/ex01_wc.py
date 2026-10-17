"""Exercício 1: um mini "wc" com argparse."""
import argparse


def count_text(text: str) -> tuple[int, int, int]:
    """Devolva ``(linhas, palavras, caracteres)`` de ``text``.

    Linhas: quantidade de ``"\\n"``. Palavras: ``text.split()``.
    Exemplo: ``count_text("a b\\nc\\n") == (2, 3, 6)``.
    """
    raise NotImplementedError


def build_parser() -> argparse.ArgumentParser:
    """Monte o parser: argumentos posicionais ``files`` (um ou mais) e
    as flags ``-l/--lines``, ``-w/--words`` e ``-c/--chars``.
    Dica: ``nargs="+"`` e ``action="store_true"``.
    """
    raise NotImplementedError


def main(argv: list[str] | None = None) -> int:
    """Para cada arquivo (UTF-8), imprima ``<contagens> <arquivo>``.

    Sem nenhuma flag, imprima as três contagens (linhas palavras chars).
    Com flags, imprima só as pedidas, sempre nessa ordem.
    Arquivo inexistente: imprima ``wc: <arquivo>: not found`` em
    ``sys.stderr``, continue com os outros e devolva 1 no final.
    Devolva 0 se tudo deu certo.
    """
    raise NotImplementedError


if __name__ == "__main__":
    raise SystemExit(main())
