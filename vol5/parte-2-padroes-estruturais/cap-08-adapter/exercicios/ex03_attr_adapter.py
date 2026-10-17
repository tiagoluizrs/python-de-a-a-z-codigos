"""Exercício 3: um adaptador por DELEGAÇÃO (``__getattr__``) que renomeia atributos e métodos e deixa o resto passar."""


class Renamed:
    """``Renamed(obj, mapping)``; ``mapping`` é ``{nome_novo: nome_antigo}``.

    * na criação, cada nome ANTIGO precisa existir em ``obj`` (``hasattr``): senão ``ValueError(f"atributo inexistente: {antigo}")``;
    * ler ``adapter.nome_novo`` devolve ``obj.nome_antigo`` (métodos incluídos: ``adapter.increment()`` chama ``obj.incr()``); nomes fora do mapeamento passam
      direto para ``obj``; um nome que ``obj`` não tem: ``AttributeError`` (o do próprio ``getattr``);
    * atribuir (``adapter.valor = 3``) e apagar (``del adapter.valor``) também traduzem o nome e agem sobre ``obj``;
    * ``unwrap()`` devolve o ``obj`` original (use o nome ``unwrap`` com cuidado: se ``obj`` também tiver um ``unwrap``, o do adaptador vence);
    * ``dir(adapter)`` lista os nomes de ``obj`` com os antigos mapeados SUBSTITUÍDOS pelos novos (sem duplicar), ordenados;
    * ``repr`` é ``f"Renamed({obj!r})"``.
    Cuidado: o próprio adaptador guarda ``_obj`` e ``_mapping``; use ``object.__setattr__`` para isso (senão o seu ``__setattr__`` entra em recursão)."""

    def __init__(self, obj, mapping: dict):
        raise NotImplementedError

    def __getattr__(self, name):
        raise NotImplementedError

    def __setattr__(self, name, value):
        raise NotImplementedError

    def __delattr__(self, name):
        raise NotImplementedError

    def __dir__(self):
        raise NotImplementedError

    def __repr__(self):
        raise NotImplementedError

    def unwrap(self):
        raise NotImplementedError
