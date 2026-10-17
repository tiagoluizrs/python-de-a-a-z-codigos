"""Gabarito do exercício 4."""
import re


def plan_report(conn, sql, params=()):
    scans, searches, temp = [], [], False
    for row in conn.execute("EXPLAIN QUERY PLAN " + sql, params):
        detail = row[-1]
        if detail.startswith("SCAN"):
            match = re.match(r"SCAN (?:TABLE )?(\S+)", detail)
            if match and match.group(1) != "CONSTANT":
                scans.append(match.group(1))
        elif detail.startswith("SEARCH"):
            match = re.match(r"SEARCH (?:TABLE )?(\S+) USING (?:COVERING )?(?:INTEGER PRIMARY KEY|PRIMARY KEY|INDEX (\S+))", detail)
            if match:
                searches.append((match.group(1), match.group(2) or "PRIMARY KEY"))
        if "USE TEMP B-TREE" in detail:
            temp = True
    return {"scans": sorted(scans), "searches": sorted(searches), "temp_btree": temp, "uses_index": bool(searches)}


def assert_uses_index(conn, sql, params=(), table=None):
    report = plan_report(conn, sql, params)
    bad = [t for t in report["scans"] if table is None or t == table]
    if bad:
        raise AssertionError(f"varredura completa em {', '.join(bad)}: {sql}")
