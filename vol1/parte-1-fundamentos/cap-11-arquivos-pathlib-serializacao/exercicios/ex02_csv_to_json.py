"""Exercício 2: converter CSV em JSON respeitando tipos."""
from collections.abc import Callable
from pathlib import Path


def csv_to_json(csv_path: Path, json_path: Path,
                types: dict[str, Callable]) -> int:
    """Leia ``csv_path`` e grave uma lista de objetos em ``json_path``.

    - O CSV é UTF-8, possivelmente com BOM (``utf-8-sig``), tem
      cabeçalho e pode ter campos entre aspas com vírgulas e
      quebras de linha (use o módulo ``csv`` e ``newline=""``).
    - ``types`` mapeia nome de coluna para função de conversão, por
      exemplo ``{"id": int, "price": float}``. Colunas ausentes em
      ``types`` ficam como texto.
    - Campo vazio (``""``) vira ``None`` (``null`` no JSON), sem
      chamar a função de conversão.
    - Grave com ``indent=2`` e ``ensure_ascii=False``, em UTF-8.
    - Devolva o número de linhas de dados convertidas.

    Exemplo: o CSV ``id,name\\n1,Ana\\n2,\\n`` com ``{"id": int}``
    gera ``[{"id": 1, "name": "Ana"}, {"id": 2, "name": null}]``.
    """
    raise NotImplementedError
