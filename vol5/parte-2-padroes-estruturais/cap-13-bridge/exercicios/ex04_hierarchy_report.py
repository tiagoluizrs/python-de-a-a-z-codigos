"""Exercício 4: quando o Bridge compensa? Contar classes e detectar hierarquias "cartesianas" nos nomes."""
import re


def explosion_count(m: int, n: int) -> int:
    """Classes de uma herança por combinação: ``m * n``. ``m`` ou ``n`` negativos: ``ValueError("contagem negativa")``."""
    raise NotImplementedError


def bridge_count(m: int, n: int, bases: int = 2) -> int:
    """Classes com o Bridge: ``m + n`` mais as ``bases`` (a abstração base e a interface da implementação). Mesmo ``ValueError`` de contagem negativa."""
    raise NotImplementedError


def savings(m: int, n: int) -> int:
    """``explosion_count(m, n) - bridge_count(m, n)`` (pode ser negativo: o Bridge não compensa)."""
    raise NotImplementedError


def worthwhile_pairs(max_side: int = 10) -> list[tuple[int, int]]:
    """Os pares ``(m, n)`` com ``1 <= m <= n <= max_side`` em que o Bridge usa MENOS classes que a herança por combinação (``savings > 0``), em ordem
    crescente de ``m`` e depois de ``n``."""
    raise NotImplementedError


def split_camel(name: str) -> list[str]:
    """Divide um nome em CamelCase em palavras, tratando siglas: ``"AlertEmail"`` -> ``["Alert", "Email"]``; ``"SMSAlert"`` -> ``["SMS", "Alert"]``;
    ``"HttpRequest2"`` -> ``["Http", "Request2"]``; ``"Alert"`` -> ``["Alert"]``; texto vazio -> ``[]``. (Dica: ``re.findall(r"[A-Z]+(?![a-z])|[A-Z][a-z0-9]*", nome)``.)"""
    raise NotImplementedError


def cartesian_candidates(names: list[str]) -> list[tuple[tuple[str, ...], tuple[str, ...]]]:
    """Procura sinais de explosão de classes: considere só os nomes com EXATAMENTE duas palavras (``split_camel``); agrupe as primeiras palavras (``prefixo``) pelo
    CONJUNTO exato de segundas palavras (``sufixo``) com que aparecem. Cada grupo com 2 ou mais prefixos E 2 ou mais sufixos vira um resultado
    ``(prefixos_ordenados, sufixos_ordenados)``; a lista sai ordenada pelos prefixos. Nomes repetidos contam uma vez."""
    raise NotImplementedError
