"""Exercício 2: ler uma medição de escalabilidade."""


def speedup_table(sequential, timings):
    """``timings`` é um dicionário ``{trabalhadores: tempo_em_segundos}``. Devolve uma
    lista de tuplas ``(trabalhadores, ganho, eficiência)`` ORDENADA por
    trabalhadores, com ``ganho = sequential / tempo`` e
    ``eficiência = ganho / trabalhadores``. ``sequential <= 0``, tempo <= 0 ou
    trabalhadores < 1 levantam ``ValueError``."""
    raise NotImplementedError


def best_workers(table, min_efficiency=0.5):
    """Maior número de trabalhadores cuja eficiência é >= ``min_efficiency`` e cujo
    ganho é MAIOR que o de todos os menores (o ponto em que ainda compensa). Se
    nenhuma linha atende, devolva 1. ``table`` é o resultado de ``speedup_table``."""
    raise NotImplementedError
