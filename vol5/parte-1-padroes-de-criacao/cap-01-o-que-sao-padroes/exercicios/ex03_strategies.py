"""Exercício 3: estratégias de desconto como FUNÇÕES, com combinadores (sem uma classe sequer)."""


def percent(p: float):
    """Devolve uma estratégia ``f(total) -> float`` que aplica ``p`` por cento de desconto (``total * (1 - p/100)``).
    ``p`` fora de 0 a 100: ``ValueError("percentual inválido: ...")`` (levantado ao CRIAR a estratégia, não ao usá-la)."""
    raise NotImplementedError


def fixed(amount: float):
    """Estratégia que subtrai ``amount`` do total, sem passar de zero (nunca devolve negativo). ``amount < 0``: ``ValueError``."""
    raise NotImplementedError


def tiered(*tiers: tuple[float, float]):
    """Estratégia por faixas: cada faixa é ``(minimo, percentual)``. Aplica o percentual da MAIOR faixa cujo ``minimo <= total``;
    se nenhuma serve, devolve o total sem desconto. Sem faixas: ``ValueError``."""
    raise NotImplementedError


def best_of(*strategies):
    """Combina estratégias: devolve uma estratégia que aplica TODAS ao mesmo total e fica com o MENOR resultado (o maior desconto).
    Sem estratégias: ``ValueError``."""
    raise NotImplementedError


def then(*strategies):
    """Encadeia estratégias: a saída de uma é a entrada da seguinte, na ordem dada. Sem estratégias: devolve a identidade."""
    raise NotImplementedError


def checkout(subtotal: float, strategy=None) -> float:
    """``round(strategy(subtotal), 2)``; sem estratégia, o próprio subtotal arredondado. ``subtotal < 0``: ``ValueError``."""
    raise NotImplementedError
