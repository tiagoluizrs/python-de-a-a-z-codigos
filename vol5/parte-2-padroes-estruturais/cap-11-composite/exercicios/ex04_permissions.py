"""Exercício 4: um Composite de PERMISSÕES: papéis (``Role``) que contêm permissões (folhas) e outros papéis (galhos), sem ciclos."""


class RoleRegistry:
    """Guarda papéis. Um papel tem um ``name``, um conjunto de permissões próprias (textos) e uma lista de papéis que ele INCLUI (herda).

    * ``define(name, permissions=(), includes=())``: cria o papel. Nome já usado: ``ValueError(f"role já existe: {name}")``; algum ``includes`` desconhecido:
      ``ValueError(f"role desconhecida: {nome}")`` (o primeiro desconhecido, na ordem dada);
    * ``include(name, other)``: acrescenta ``other`` aos papéis incluídos por ``name``. Papéis desconhecidos: ``KeyError(nome)`` (``name`` primeiro). Se isso
      criaria um CICLO (``other`` já inclui ``name``, direta ou indiretamente, ou ``other == name``), ``ValueError(f"ciclo: {a} -> {b} -> ...")`` mostrando o
      caminho: ``name -> other -> ... -> name`` (o caminho mais curto de ``other`` até ``name`` pelos ``includes``, com desempates em ordem alfabética);
    * ``permissions(role)``: o conjunto ORDENADO (``sorted``, em lista) de todas as permissões do papel, incluindo as dos papéis incluídos, em qualquer
      profundidade (cada papel é visitado uma vez, mesmo em losango); desconhecido: ``KeyError(role)``;
    * ``can(role, permission)``: ``permission in permissions(role)``;
    * ``explain(role, permission)``: o caminho MAIS CURTO de papéis (``list``) de ``role`` até um papel que tem a permissão como PRÓPRIA, por busca em largura visitando
      os incluídos em ordem alfabética; ``None`` se o papel não a tem. ``[role]`` se é própria do próprio papel;
    * ``roles_with(permission)``: os nomes (ordenados) dos papéis que têm a permissão (própria ou herdada)."""

    def define(self, name: str, permissions=(), includes=()) -> None:
        raise NotImplementedError

    def include(self, name: str, other: str) -> None:
        raise NotImplementedError

    def permissions(self, role: str) -> list[str]:
        raise NotImplementedError

    def can(self, role: str, permission: str) -> bool:
        raise NotImplementedError

    def explain(self, role: str, permission: str):
        raise NotImplementedError

    def roles_with(self, permission: str) -> list[str]:
        raise NotImplementedError
