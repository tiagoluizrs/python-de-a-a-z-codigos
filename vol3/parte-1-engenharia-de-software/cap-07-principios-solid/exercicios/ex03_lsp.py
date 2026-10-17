"""Exercício 3 (L): uma subclasse que HONRA o contrato de ``MutableMapping`` em todos os caminhos."""
from collections.abc import MutableMapping


class LimitedDict(MutableMapping):
    """Um dicionário com duas regras EXTRAS, aplicadas em TODOS os caminhos de escrita (``d[k] = v``, ``update``, ``setdefault``, o construtor...
    tudo o que a ``MutableMapping`` oferece em cima de ``__setitem__``):

    * ``max_items``: no máximo essa quantidade de chaves; tentar acrescentar uma chave NOVA com o dicionário cheio levanta
      ``OverflowError("dicionário cheio")`` e NÃO altera nada (atualizar o valor de uma chave que já existe é sempre permitido);
    * ``validator(value) -> bool``: se for dado e devolver falso para um valor, ``ValueError(f"valor inválido: {value!r}")``, sem alterar nada.

    ``LimitedDict(max_items=3, validator=None, initial=None)``: ``initial`` (um dict ou iterável de pares) entra pelo MESMO caminho de
    validação; se ``max_items < 1``: ``ValueError``.

    Contrato herdado (não pode ser quebrado): ``len``, ``in``, iteração na ORDEM de inserção, ``del d[k]`` (``KeyError`` se ausente),
    ``d[k]`` (``KeyError`` se ausente), ``pop``, ``popitem``, ``clear``, ``get``, ``keys/values/items``, ``==`` com um ``dict`` comum de mesmo
    conteúdo, e ``copy()`` devolvendo um ``LimitedDict`` NOVO com as mesmas regras e o mesmo conteúdo (independente do original).
    Implemente só o que a ``MutableMapping`` exige (``__getitem__``, ``__setitem__``, ``__delitem__``, ``__iter__``, ``__len__``) mais
    ``copy``; deixe o resto vir da classe base: é assim que a regra vale em todos os caminhos."""

    def __init__(self, max_items: int = 3, validator=None, initial=None):
        raise NotImplementedError

    def __getitem__(self, key):
        raise NotImplementedError

    def __setitem__(self, key, value):
        raise NotImplementedError

    def __delitem__(self, key):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

    def copy(self):
        raise NotImplementedError
