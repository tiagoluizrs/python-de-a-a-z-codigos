"""Exercício 6: auditoria simples de dependências."""


def release(text):
    return tuple(int(part) for part in text.split("."))


def vulnerable(installed, advisories):
    """``installed``: ``{nome: versão}``. ``advisories``: lista de dicts
    ``{"id": "X-1", "name": "pacote", "below": "2.0.1"}`` significando "versões
    ESTRITAMENTE menores que ``below`` são vulneráveis".

    Devolve a lista ordenada por ``(nome, id)`` de dicts
    ``{"id", "name", "installed", "fix": below}`` dos achados. Nomes
    comparados SEM diferenciar maiúsculas e tratando ``_`` e ``-`` como iguais.
    Versões comparadas numericamente."""
    raise NotImplementedError


def distance(a, b):
    """Distância de edição de Levenshtein entre duas strings."""
    raise NotImplementedError


def suspicious(candidates, popular, max_distance=1):
    """Nomes de ``candidates`` que NÃO são populares, mas estão a no máximo
    ``max_distance`` edições de algum nome em ``popular`` (possível
    *typosquatting*). Devolve a lista ordenada de pares ``(candidato,
    popular_parecido)``; se parecer com mais de um, o de menor distância
    (empate: o primeiro em ordem alfabética). Compare em minúsculas."""
    raise NotImplementedError
