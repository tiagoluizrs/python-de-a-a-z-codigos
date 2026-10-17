"""Gabarito do exercício 2."""

_REGISTRY: dict = {}


class UnknownShippingMethod(Exception):
    pass


def shipping_method(name, **options):
    if not name:
        raise ValueError("nome vazio")
    min_price = options.get("min_price", 0.0)

    def register(fn):
        if name in _REGISTRY:
            raise ValueError(f"método já registrado: {name}")
        _REGISTRY[name] = (fn, min_price)
        return fn

    return register


def shipping_cost(method, weight_kg, distance_km):
    if weight_kg <= 0 or distance_km < 0:
        raise ValueError("peso deve ser positivo e distância não negativa")
    if method not in _REGISTRY:
        raise UnknownShippingMethod(f"método desconhecido: {method}")
    fn, min_price = _REGISTRY[method]
    return round(max(fn(weight_kg, distance_km), min_price), 2)


def available_methods():
    return sorted(_REGISTRY)


def cheapest(weight_kg, distance_km):
    if not _REGISTRY:
        raise UnknownShippingMethod("nenhum método registrado")
    return min(((name, shipping_cost(name, weight_kg, distance_km)) for name in sorted(_REGISTRY)), key=lambda item: item[1])


def reset_registry():
    _REGISTRY.clear()
