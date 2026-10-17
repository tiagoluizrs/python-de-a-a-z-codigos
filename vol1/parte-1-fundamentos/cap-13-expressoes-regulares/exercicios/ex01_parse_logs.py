"""Exercício 1: extrair nível, timestamp e mensagem de logs."""


def parse_logs(text: str) -> list[dict[str, str]]:
    """Devolva um dicionário por linha de log válida em ``text``.

    Formato: ``AAAA-MM-DD HH:MM:SS [NIVEL] mensagem``, onde o separador
    entre data e hora pode ser espaço ou ``T``. Cada dicionário tem as
    chaves ``timestamp``, ``level`` e ``message``. Linhas que não seguem
    o formato são ignoradas.

    Exemplo::

        parse_logs("2026-10-12 14:03:22 [INFO] started")
        == [{"timestamp": "2026-10-12 14:03:22",
             "level": "INFO", "message": "started"}]

    Dicas: grupos nomeados, ``re.MULTILINE`` e ``finditer``.
    """
    raise NotImplementedError
