"""Exercício 5: serializar dataclasses com fields() e metadata."""


def to_primitive(value):
    """Converta ``value`` em estruturas JSON-friendly (dict, list, str, int,
    float, bool, None).

    * dataclass -> ``dict`` com os campos, EXCETO os marcados com
      ``metadata={"skip": True}``; use ``dataclasses.fields`` (não ``asdict``);
      o nome de saída é ``metadata["name"]`` se existir, senão o do campo;
    * ``Decimal`` -> ``str``;
    * ``date``/``datetime`` -> ``isoformat()``;
    * ``list``/``tuple``/``set`` -> ``list`` (sets ORDENADOS por ``str``);
    * ``dict`` -> ``dict`` com valores convertidos e chaves ``str``;
    * ``Enum`` -> o ``value``;
    * demais tipos básicos (``str``, ``int``, ``float``, ``bool``, ``None``)
      ficam como estão; outros tipos levantam ``TypeError``.
    """
    raise NotImplementedError
