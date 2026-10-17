"""Exercício 5: decorador que valida tipos a partir das anotações."""


def validate_types(func):
    """Verifica em tempo de execução os argumentos anotados com classes.

    Use ``inspect.signature(func).bind(...)`` para associar os valores
    aos nomes e ``typing.get_type_hints(func)`` para ler as anotações.

    - para cada parâmetro anotado com uma CLASSE (``int``, ``str``,
      ``list``...), exija ``isinstance(valor, classe)``; senão levante
      ``TypeError("<param> must be <classe>, got <tipo do valor>")``,
      por exemplo ``"age must be int, got str"``;
    - anotações que não são classes (``int | None``, ``list[int]``...)
      são ignoradas; parâmetros sem anotação também;
    - aplique os valores padrão (``bind(...).apply_defaults()``) para
      validar também os parâmetros omitidos;
    - ``bool`` conta como ``int`` (é uma subclasse), sem tratamento
      especial;
    - não valide o retorno; preserve os metadados com ``wraps``.
    """
    raise NotImplementedError
