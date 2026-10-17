"""Exercício 3: singledispatch."""


def describe(value):
    """Use ``functools.singledispatch`` (a função exportada precisa ter o
    atributo ``register``). Regras:

    * ``bool`` -> ``"yes"`` ou ``"no"`` (cuidado: ``bool`` é subclasse de ``int``);
    * ``int`` -> ``"int(<valor>)"``;
    * ``float`` -> ``"float(<valor com 1 casa decimal>)"``;
    * ``str`` -> o texto entre aspas simples (``"'abc'"``);
    * ``None`` -> ``"nothing"``  (dica: registre ``type(None)``);
    * ``list``/``tuple``/``set`` -> ``"[...]"`` com os itens descritos e
      separados por vírgula e espaço (sets ORDENADOS pelo texto descrito);
    * ``dict`` -> ``"{k: v, ...}"`` com chaves e valores descritos,
      na ordem de inserção;
    * qualquer outro tipo -> ``"<NomeDoTipo>"``.
    """
    raise NotImplementedError
