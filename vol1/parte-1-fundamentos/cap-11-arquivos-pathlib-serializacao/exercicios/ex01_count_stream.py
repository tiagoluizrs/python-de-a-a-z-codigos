"""Exercício 1: contar linhas, palavras e caracteres em streaming."""
from pathlib import Path


def count_stream(path: Path) -> tuple[int, int, int]:
    """Devolva ``(linhas, palavras, caracteres)`` do arquivo UTF-8.

    - Linha: cada trecho terminado em ``\\n`` (a última linha conta
      mesmo sem ``\\n`` no final). Arquivo vazio tem 0 linhas.
    - Palavra: sequência separada por espaços em branco (``str.split``).
    - Caracteres: total de caracteres, incluindo as quebras de linha,
      lidas com ``newline=""`` para não traduzir ``\\r\\n``.

    Restrição: o arquivo pode ser maior que a memória. Leia linha a
    linha (ou em blocos); NÃO use ``read()`` nem ``readlines()``.
    Os testes medem o pico de memória com ``tracemalloc``.
    """
    raise NotImplementedError
