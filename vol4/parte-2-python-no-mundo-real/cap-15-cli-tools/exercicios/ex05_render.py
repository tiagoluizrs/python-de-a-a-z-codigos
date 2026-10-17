"""Exercício 5: uma saída que serve a pessoas e a programas (tabela, JSON, CSV, texto) e respeita NO_COLOR."""


def render(rows: list[dict], fmt: str, color: bool = False, width: int = 80) -> str:
    """Devolve o texto das ``rows`` (lista de dicts com as MESMAS chaves, na mesma ordem) no formato ``fmt``:

    * ``"json"``: ``json.dumps(rows, ensure_ascii=False)`` (uma linha);
    * ``"csv"``: cabeçalho + uma linha por registro, separador ``,``, quebra de linha ``\\n``, ``csv.writer``; valores
      com vírgula são aspados pelo próprio ``csv``;
    * ``"plain"``: uma linha por registro, os valores separados por TAB (``\\t``), sem cabeçalho (para ``cut``/``awk``);
    * ``"table"``: uma tabela do Rich (``rich.table.Table``) com uma coluna por chave (título = a chave), renderizada em
      um ``Console`` de largura ``width`` gravando em um ``io.StringIO``; com ``color=False`` o texto NÃO pode ter
      nenhum código ANSI (``"\\x1b"``); com ``color=True``, deve ter (``force_terminal=True``). Sem registros:
      devolva ``"(vazio)"``;
    * qualquer outro formato: ``ValueError(f"formato desconhecido: {fmt!r}")``.

    Nenhum formato termina com quebra de linha extra: ``str.rstrip("\\n")`` no resultado."""
    raise NotImplementedError


def want_color(mode: str, is_tty: bool, env: dict) -> bool:
    """Decide se usa cor: ``"always"`` -> ``True``; ``"never"`` -> ``False``; ``"auto"`` -> ``True`` só se ``is_tty`` e
    a variável ``NO_COLOR`` NÃO estiver em ``env`` (qualquer valor, até vazio, conta como definida); outro ``mode``:
    ``ValueError``."""
    raise NotImplementedError
