"""Exercício 2: normalizar eventos (dicionários) com match de mapeamento."""


def normalize(event: dict) -> dict:
    """Converta um evento bruto em um evento normalizado.

    - ``{"type": "click", "x": 1, "y": 2}``
      -> ``{"kind": "click", "pos": (1, 2)}`` (x e y devem ser ``int``)
    - ``{"type": "key", "key": "A"}``
      -> ``{"kind": "key", "key": "a"}`` (``key`` deve ser ``str``)
    - ``{"type": "scroll", "dy": 3}``
      -> ``{"kind": "scroll", "delta": 3}`` (``dy`` deve ser ``int``)
    - chaves extras são ignoradas.
    - qualquer outra coisa (inclusive não-dict, tipos errados ou
      chaves ausentes) -> ``ValueError``.
    """
    raise NotImplementedError
