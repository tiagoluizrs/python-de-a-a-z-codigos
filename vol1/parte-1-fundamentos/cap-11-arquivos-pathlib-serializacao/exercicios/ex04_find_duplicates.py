"""Exercício 4: encontrar arquivos duplicados por conteúdo."""
from pathlib import Path


def find_duplicates(root: Path) -> list[list[Path]]:
    """Devolva grupos de arquivos com conteúdo idêntico sob ``root``.

    - Percorra a árvore inteira com ``pathlib`` (``rglob`` ou ``walk``);
      considere apenas arquivos regulares (``is_file()``).
    - Agrupe primeiro por tamanho (barato, ``stat().st_size``) e só
      calcule o hash (``hashlib.sha256``) dos arquivos que tenham
      tamanho em comum. Leia em blocos de 64 KiB: nada de ``read()``
      do arquivo inteiro.
    - Cada grupo tem 2 ou mais caminhos, ordenados. Os grupos são
      ordenados pelo primeiro caminho. Arquivos únicos não aparecem.
    - Arquivos vazios são todos iguais entre si.
    """
    raise NotImplementedError
