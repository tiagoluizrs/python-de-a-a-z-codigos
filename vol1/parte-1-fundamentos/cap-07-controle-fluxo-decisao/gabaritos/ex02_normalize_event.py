"""Gabarito 2: normalizar eventos com padrões de mapeamento."""


def normalize(event: dict) -> dict:
    # Mapeamentos ignoram chaves extras; str()/int() checam o tipo.
    match event:
        case {"type": "click", "x": int(x), "y": int(y)}:
            return {"kind": "click", "pos": (x, y)}
        case {"type": "key", "key": str(key)}:
            return {"kind": "key", "key": key.lower()}
        case {"type": "scroll", "dy": int(dy)}:
            return {"kind": "scroll", "delta": dy}
        case _:
            raise ValueError(f"invalid event: {event!r}")
