"""Exercício 2 (O): um cálculo de frete ABERTO para extensão: novos métodos de entrega são registrados, nunca editados na função."""


class UnknownShippingMethod(Exception):
    pass


def shipping_method(name: str, **options):
    """Decorador de registro: ``@shipping_method("sedex")`` registra a função decorada como o cálculo do método ``name``.

    * a função registrada recebe ``(weight_kg: float, distance_km: float)`` e devolve o preço (``float``);
    * ``options`` opcionais: ``min_price`` (``float``, preço mínimo: o resultado nunca é menor que isso; padrão ``0.0``);
    * registrar um nome que já existe: ``ValueError(f"método já registrado: {name}")``; nome vazio: ``ValueError``;
    * o decorador devolve a PRÓPRIA função (para poder ser chamada diretamente)."""
    raise NotImplementedError


def shipping_cost(method: str, weight_kg: float, distance_km: float) -> float:
    """O preço do frete (``round(..., 2)``) pelo método registrado, respeitando ``min_price``. Método desconhecido:
    ``UnknownShippingMethod(f"método desconhecido: {method}")``. ``weight_kg <= 0`` ou ``distance_km < 0``: ``ValueError`` (ANTES de
    procurar o método). Esta função NUNCA deve ser editada quando um método novo aparece."""
    raise NotImplementedError


def available_methods() -> list[str]:
    """Os nomes registrados, em ordem alfabética."""
    raise NotImplementedError


def cheapest(weight_kg: float, distance_km: float) -> tuple[str, float]:
    """O ``(nome, preço)`` do método mais barato para esses valores (empate: o menor nome em ordem alfabética). Sem métodos
    registrados: ``UnknownShippingMethod("nenhum método registrado")``."""
    raise NotImplementedError


def reset_registry() -> None:
    """Esvazia o registro (para os testes isolarem uns dos outros)."""
    raise NotImplementedError
