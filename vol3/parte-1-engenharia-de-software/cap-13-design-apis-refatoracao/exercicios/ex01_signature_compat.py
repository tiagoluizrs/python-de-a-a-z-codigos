"""Exercício 1: detectar mudanças que quebram quem já usa uma função."""


def breaking_changes(old, new):
    """Compara as assinaturas de ``old`` e ``new`` (callables; ``inspect.signature``)
    e devolve a lista ORDENADA de textos, um por incompatibilidade, para quem
    chamava ``old``:

    * ``"removed: <nome>"``: um parâmetro de ``old`` sumiu (e ``new`` não tem
      ``**kwargs`` para absorvê-lo, nem ``*args`` se era posicional);
    * ``"new-required: <nome>"``: ``new`` tem um parâmetro obrigatório (sem padrão,
      que não seja ``*args``/``**kwargs``) que ``old`` não tinha;
    * ``"reordered: <nome>"``: um parâmetro que aceitava posição mudou de posição
      relativa entre os posicionais que os dois têm;
    * ``"kind: <nome>"``: o parâmetro passou de posicional-ou-nomeado para
      SÓ-NOMEADO (ou para só-posicional, se era chamável por nome);
    * ``"lost-default: <nome>"``: tinha padrão e deixou de ter.

    Mudanças compatíveis (parâmetro novo com padrão, padrão alterado, anotações,
    parâmetro só-nomeado que passou a aceitar posição) NÃO contam. Uma função
    compatível devolve ``[]``."""
    raise NotImplementedError
