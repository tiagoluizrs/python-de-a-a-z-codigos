"""Exercício 5: limitador de taxa (token bucket), seguro entre threads."""
import time


class RateLimiter:
    """Balde de fichas: ``rate`` fichas por segundo, capacidade ``burst``.

    * ``RateLimiter(rate, burst, clock=time.monotonic, sleep=time.sleep)``; começa
      CHEIO (``burst`` fichas); ``rate <= 0`` ou ``burst < 1`` levantam ``ValueError``;
    * fichas se acumulam com o tempo (``rate * decorrido``), no máximo ``burst``;
    * ``try_acquire(n=1)``: se houver ``n`` fichas, consome e devolve ``True``;
      senão ``False`` sem consumir (``n > burst`` levanta ``ValueError``);
    * ``acquire(n=1)``: espera (com ``sleep``) o tempo necessário e consome;
      devolve quantos segundos ESPEROU (``0.0`` se havia fichas);
    * seguro entre threads (use uma trava, e NÃO durma segurando a trava)."""

    def __init__(self, rate, burst, clock=time.monotonic, sleep=time.sleep):
        raise NotImplementedError
