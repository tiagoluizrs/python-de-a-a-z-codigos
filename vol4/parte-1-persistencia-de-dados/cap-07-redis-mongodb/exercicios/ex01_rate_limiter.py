"""Exercício 1: limite de taxa por janela fixa no Redis."""


class FixedWindowLimiter:
    """``FixedWindowLimiter(redis, limit, window_ms, prefix="rl")``.

    ``allow(key)`` -> ``(permitido, restantes, retry_after_ms)``:

    * conta os pedidos de ``key`` na janela com a chave Redis ``f"{prefix}:{key}"``;
    * a PRIMEIRA contagem da janela define a expiração (``PEXPIRE`` ``window_ms``) e a janela
      NÃO é renovada pelos pedidos seguintes;
    * ``permitido`` é ``True`` enquanto a contagem ``<= limit``; ``restantes = max(0, limit - contagem)``;
    * ``retry_after_ms`` é ``0`` se permitido; senão o ``PTTL`` da chave (tempo até a janela virar);
    * a contagem + expiração devem ser ATÔMICAS (um script Lua com ``register_script``, ou
      ``INCR`` e ``PEXPIRE ... NX`` em pipeline); com 8 clientes simultâneos, o total de permitidos
      NUNCA passa de ``limit``;
    * ``limit < 1`` ou ``window_ms < 1`` levantam ``ValueError``."""

    def __init__(self, redis, limit, window_ms, prefix="rl"):
        raise NotImplementedError
