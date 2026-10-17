"""Exercício 1: o grafo de revisões (o coração do Alembic, em Python puro)."""


def analyze_revisions(revisions):
    """``revisions`` é um dicionário ``{revisão: pai}`` onde ``pai`` é ``None`` (revisão base),
    uma ``str`` ou uma ``tuple`` de ``str`` (revisão de MERGE, com vários pais).

    Devolve ``{"bases": [...], "heads": [...], "order": [...]}``:

    * ``bases``: revisões sem pai, em ordem alfabética;
    * ``heads``: revisões que NÃO são pai de ninguém, em ordem alfabética;
    * ``order``: ordem topológica (pais antes dos filhos); entre as prontas, escolha sempre a
      de MENOR id (ordem alfabética), para o resultado ser determinístico;
    * pai que não existe em ``revisions`` levanta ``ValueError``; ciclo levanta ``ValueError``;
      dicionário vazio devolve listas vazias."""
    raise NotImplementedError


def upgrade_path(revisions, current, target):
    """Revisões a APLICAR para ir de ``current`` (``None`` = banco vazio) até ``target``, em ordem:
    todos os ancestrais de ``target`` (inclusive ele) que NÃO são ``current`` nem ancestrais
    de ``current``, na ordem de ``analyze_revisions(revisions)["order"]``.

    * ``current == target`` devolve ``[]``;
    * revisão desconhecida (``current`` ou ``target``) levanta ``ValueError``;
    * se ``current`` NÃO for ancestral de ``target`` (branches diferentes), apenas desconte os
      ancestrais de ``current`` (o Alembic exigiria um merge, mas aqui só calculamos)."""
    raise NotImplementedError
