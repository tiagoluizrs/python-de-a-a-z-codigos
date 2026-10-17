"""Exercício 2: fábricas de flyweights com as ferramentas da biblioteca padrão: ``functools.lru_cache`` e ``weakref.WeakValueDictionary``."""
import functools
import weakref
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Color:
    """``r``, ``g`` e ``b`` inteiros de 0 a 255 (``bool`` não vale). Fora do intervalo ou de outro tipo: ``ValueError(f"componente inválido: {nome}={valor!r}")``
    (verifique na ordem ``r``, ``g``, ``b``; o ``nome`` é a letra)."""

    r: int
    g: int
    b: int

    def __post_init__(self):
        raise NotImplementedError


class ColorPool:
    """``ColorPool(maxsize=128)``: uma fábrica com cache LIMITADO.

    * ``color(r, g, b)`` devolve o MESMO ``Color`` para os mesmos valores enquanto estiver no cache (use ``functools.lru_cache(maxsize=maxsize)``, criado na
      INSTÂNCIA: dois ``ColorPool`` não compartilham cache); os valores inválidos levantam o ``ValueError`` do ``Color`` e não entram no cache;
    * ``info()``: ``{"hits": n, "misses": n, "size": n, "maxsize": n}`` (de ``cache_info()``);
    * ``clear()``: esvazia o cache e zera as estatísticas (``cache_clear``);
    * ``maxsize`` menor que 1: ``ValueError("maxsize deve ser >= 1")``."""

    def __init__(self, maxsize: int = 128):
        raise NotImplementedError

    def color(self, r: int, g: int, b: int) -> Color:
        raise NotImplementedError

    def info(self) -> dict:
        raise NotImplementedError

    def clear(self) -> None:
        raise NotImplementedError


class WeakPool:
    """``WeakPool(factory)``: um pool que NÃO impede a coleta: guarda os objetos em um ``weakref.WeakValueDictionary``.

    * ``get(key)``: devolve o objeto vivo para ``key`` ou cria um com ``factory(key)`` (e o guarda); duas chamadas seguidas com a mesma chave, com o objeto ainda
      referenciado por alguém, devolvem o MESMO objeto;
    * quando ninguém mais referencia o objeto, ele some do pool (``len(pool)`` diminui) e o próximo ``get(key)`` cria outro; ``factory`` precisa devolver objetos
      que aceitem referência fraca (instâncias de classes comuns; ``int``, ``str`` e ``tuple`` NÃO aceitam: o ``TypeError`` do ``weakref`` sobe);
    * ``len(pool)`` e ``key in pool`` consideram só os vivos; ``stats``: ``{"created": n, "reused": n}`` (acumulados)."""

    def __init__(self, factory):
        raise NotImplementedError

    def get(self, key):
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError

    def __contains__(self, key) -> bool:
        raise NotImplementedError

    @property
    def stats(self) -> dict:
        raise NotImplementedError
