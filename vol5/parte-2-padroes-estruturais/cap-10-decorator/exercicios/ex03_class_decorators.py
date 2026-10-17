"""Exercício 3: decoradores de CLASSE: recebem uma classe e devolvem a mesma classe (alterada)."""


def auto_repr(cls):
    """Acrescenta a ``cls`` um ``__repr__`` que mostra os atributos de instância (``vars(self)``) em ORDEM ALFABÉTICA: ``Nome(a=1, b='x')``, com o ``repr``
    de cada valor e o nome da classe REAL da instância (``type(self).__name__``, para as subclasses). Se a classe já define ``__repr__`` no próprio corpo
    (``"__repr__" in vars(cls)``), NÃO o substitui. Devolve ``cls``."""
    raise NotImplementedError


def register_in(registry: dict, name: str | None = None):
    """Fábrica de decoradores: guarda a classe decorada em ``registry`` sob ``name`` (ou ``cls.__name__``) e a devolve. Nome já usado:
    ``ValueError(f"nome já registrado: {nome}")``."""
    raise NotImplementedError


def write_once(*names: str):
    """Fábrica de decoradores: os atributos de instância com esses ``names`` só podem ser ATRIBUÍDOS UMA VEZ (normalmente no ``__init__``); uma segunda
    atribuição levanta ``AttributeError(f"{nome} já foi definido")``. Os outros atributos são livres. Apagar (``del``) um desses atributos também levanta
    ``AttributeError(f"{nome} não pode ser apagado")``. Implemente com ``__setattr__`` e ``__delattr__`` acrescentados à classe (chamando o da classe
    base, ``super()``/``object``, para a atribuição de fato). Devolve a classe."""
    raise NotImplementedError


def add_methods(**methods):
    """Fábrica de decoradores: acrescenta à classe cada função de ``methods`` como método (``nome=função``). Se a classe JÁ tem um atributo com esse nome
    (no próprio corpo ou herdado): ``ValueError(f"{nome} já existe em {cls.__name__}")`` e NADA é acrescentado (valide tudo antes de alterar). Devolve a classe."""
    raise NotImplementedError
