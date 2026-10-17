"""Exercício 2: cache-aside com proteção contra a manada."""


class CacheAside:
    """``CacheAside(redis, loader, ttl_seconds=30, prefix="cache", lock_ms=2000)`` com ``redis`` criado
    com ``decode_responses=True``.

    * ``get(key)``: se ``f"{prefix}:{key}"`` existe, devolve ``json.loads`` do valor (``hits += 1``);
      senão (``misses += 1``) chama ``loader(key)``, guarda ``json.dumps`` com ``ex=ttl_seconds`` e
      devolve o valor;
    * PROTEÇÃO DA MANADA: vários ``get`` simultâneos da mesma chave fria devem chamar o ``loader``
      UMA ÚNICA vez: quem pega a trava ``f"{prefix}:lock:{key}"`` (``SET NX PX lock_ms``) carrega; os
      outros esperam em laço curto (``time.sleep(0.01)``) até o valor aparecer no cache (e então
      contam como ``hits``); se a trava expirar sem valor, tentam de novo;
    * a trava é solta (``DEL``) ao terminar, mesmo se o ``loader`` levantar (a exceção sobe);
    * ``invalidate(key)`` apaga o valor e devolve ``True`` se existia;
    * atributos ``hits`` e ``misses`` (protegidos por ``threading.Lock``)."""

    def __init__(self, redis, loader, ttl_seconds=30, prefix="cache", lock_ms=2000):
        raise NotImplementedError
