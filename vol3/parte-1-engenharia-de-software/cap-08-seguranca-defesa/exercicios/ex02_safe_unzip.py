"""Exercício 2: extrair um zip não confiável com defesas."""
from pathlib import Path


def safe_extract_zip(zip_path, dest, *, max_files=100, max_total_bytes=10_000_000, max_ratio=100):
    """Extrai ``zip_path`` em ``dest`` e devolve a lista ORDENADA dos nomes
    (com ``/``) dos ARQUIVOS extraídos.

    Faça TODAS as verificações ANTES de escrever qualquer arquivo; se alguma
    falhar, levante ``ValueError`` e não extraia nada:

    * mais de ``max_files`` entradas;
    * nome absoluto, com ``..`` que escape de ``dest``, ou byte nulo;
    * soma dos ``file_size`` maior que ``max_total_bytes``;
    * razão ``file_size / compress_size`` maior que ``max_ratio`` em alguma
      entrada (bomba de compressão; ``compress_size == 0`` com ``file_size > 0``
      também é recusado).

    Diretórios (nomes terminados em ``/``) são criados e não entram na lista.
    Crie as pastas pai necessárias. ``dest`` pode não existir."""
    raise NotImplementedError
