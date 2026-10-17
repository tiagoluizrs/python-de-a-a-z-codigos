"""Exercício 5: um detector de segredos em texto."""


def mask(value):
    """Mascara um segredo para exibição: se tiver 8 ou mais caracteres, os 2
    primeiros + ``"*" * (n - 4)`` + os 2 últimos; se tiver menos, só ``"*" * n``."""
    raise NotImplementedError


def scan_text(text):
    """Procura segredos, linha a linha (linhas numeradas de 1). Devolve a lista de
    dicts ``{"line": n, "kind": tipo, "match": trecho_mascarado}`` em ordem de
    linha. Tipos:

    * ``"aws-access-key"``: ``AKIA`` + 16 maiúsculas/dígitos;
    * ``"private-key"``: ``-----BEGIN ... PRIVATE KEY-----``;
    * ``"jwt"``: três blocos base64url separados por ``.``, o primeiro começando por ``eyJ``;
    * ``"assignment"``: ``password``, ``secret``, ``token``, ``api_key`` (ou
      ``api-key``) = um texto ENTRE ASPAS com 8+ caracteres, sem diferenciar caixa
      — EXCETO se o texto contiver (sem diferenciar caixa) ``changeme``, ``your-``,
      ``<``, ``${`` ou ``example``.

    ``match`` é ``mask(...)`` do trecho encontrado (para ``assignment``, só o VALOR
    entre aspas). Uma linha pode ter mais de um achado; no máximo um por tipo."""
    raise NotImplementedError
