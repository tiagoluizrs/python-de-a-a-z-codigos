"""Exercício 6: ler o plano de execução e dimensionar um pool."""
import math  # noqa: F401


def plan_nodes(conn, sql, params=()):
    """Roda ``EXPLAIN (FORMAT JSON) <sql>`` (SEM ANALYZE: não executa a consulta) e devolve o
    CONJUNTO de ``Node Type`` de todos os nós do plano (percorra ``Plans`` recursivamente).
    ``conn`` usa ``dict_row``: o plano está em ``row["QUERY PLAN"][0]["Plan"]``."""
    raise NotImplementedError


def uses_index(nodes):
    """``True`` se algum nó for ``Index Scan``, ``Index Only Scan`` ou ``Bitmap Index Scan``."""
    raise NotImplementedError


def pool_size(requests_per_second, query_seconds, headroom=1.5, max_connections=100):
    """Tamanho sugerido do pool pela lei de Little: ``ceil(rps * query_seconds * headroom)``,
    no mínimo 1, e nunca mais que ``max_connections``. Valores ``<= 0`` em ``rps`` ou
    ``query_seconds``, ``headroom < 1`` ou ``max_connections < 1`` levantam ``ValueError``."""
    raise NotImplementedError
