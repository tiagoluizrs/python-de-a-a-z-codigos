"""Gabarito do exercício 6."""
import math


def plan_nodes(conn, sql, params=()):
    plan = conn.execute("EXPLAIN (FORMAT JSON) " + sql, params).fetchone()["QUERY PLAN"][0]["Plan"]
    nodes = set()

    def walk(node):
        nodes.add(node["Node Type"])
        for child in node.get("Plans", []):
            walk(child)

    walk(plan)
    return nodes


def uses_index(nodes):
    return bool(nodes & {"Index Scan", "Index Only Scan", "Bitmap Index Scan"})


def pool_size(requests_per_second, query_seconds, headroom=1.5, max_connections=100):
    if requests_per_second <= 0 or query_seconds <= 0 or headroom < 1 or max_connections < 1:
        raise ValueError("parâmetros inválidos")
    return min(max_connections, max(1, math.ceil(requests_per_second * query_seconds * headroom)))
