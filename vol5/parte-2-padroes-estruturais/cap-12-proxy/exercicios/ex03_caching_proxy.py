"""Exercício 3: um proxy de CACHE para métodos escolhidos de um objeto, com validade (TTL) e relógio injetável."""
import time


class CachingProxy:
    """``CachingProxy(target, methods, ttl=None, clock=time.monotonic)``.

    * ``methods``: os NOMES dos métodos cujo resultado é guardado. Um nome que o alvo não tem: ``AttributeError(nome)``; um nome que existe mas não é
      chamável: ``ValueError(f"não é um método: {nome}")`` (ambos na criação);
    * ler ``proxy.nome``: se ``nome`` está em ``methods``, devolve uma função que guarda o resultado por argumentos; qualquer outro atributo (inclusive
      métodos não listados) é repassado ao alvo SEM cache;
    * a chave do cache é ``(nome, args, tuple(sorted(kwargs.items())))``; argumentos NÃO hashable: chama o alvo direto, sem guardar, e conta em
      ``"bypassed"``;
    * ``ttl`` (segundos, ``None`` = sem validade): uma entrada guardada em ``t0`` vale enquanto ``clock() - t0 < ttl``; vencida, conta como ``miss`` e é
      recalculada;
    * exceções do alvo NÃO são guardadas (sobem normalmente; contam como ``miss``);
    * ``invalidate(method=None)``: remove as entradas de um método (ou todas) e devolve quantas removeu;
    * ``stats``: propriedade que devolve uma CÓPIA de ``{"hits": n, "misses": n, "bypassed": n}``."""

    def __init__(self, target, methods, ttl: float | None = None, clock=time.monotonic):
        raise NotImplementedError

    def __getattr__(self, name):
        raise NotImplementedError

    def invalidate(self, method: str | None = None) -> int:
        raise NotImplementedError

    @property
    def stats(self) -> dict:
        raise NotImplementedError
