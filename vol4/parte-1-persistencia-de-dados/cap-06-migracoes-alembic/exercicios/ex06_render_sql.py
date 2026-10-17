"""Exercício 6: gerar o SQL de uma migração (modo offline) para um DBA revisar."""


def render_sql(config, start="base", end="head"):
    """Devolve o SQL (texto) de ``alembic upgrade <start>:<end> --sql``: use
    ``alembic.command.upgrade(config, f"{start}:{end}", sql=True)`` com ``config.output_buffer``
    apontando para um ``io.StringIO``; NÃO toca em nenhum banco. Restaure ``config.output_buffer``
    ao final."""
    raise NotImplementedError


def summarize_sql(sql):
    """Conta os comandos do ``sql`` por verbo inicial: ``{"CREATE": 2, "INSERT": 1, ...}``.
    Ignore linhas em branco e de comentário (``--``); separe os comandos por ``;``; o verbo é a
    primeira palavra em MAIÚSCULAS do comando. ``BEGIN``/``COMMIT`` contam como qualquer outro."""
    raise NotImplementedError
