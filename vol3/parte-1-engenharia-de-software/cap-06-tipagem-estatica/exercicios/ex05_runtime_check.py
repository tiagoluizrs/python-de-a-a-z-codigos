"""Exercício 5: um verificador de tipos em tempo de execução."""
from typing import Any


def conforms(value: Any, hint: Any) -> bool:
    """``True`` se ``value`` é compatível com a anotação ``hint``.

    Suporte (use ``typing.get_origin`` e ``typing.get_args``):

    * classes simples (``str``, ``bytes``, ...) por ``isinstance``; ``int``
      NÃO aceita ``bool``; ``float`` aceita ``int`` e ``float``, não ``bool``;
    * ``None`` (e ``type(None)``) só aceita ``None``; ``Any`` aceita tudo;
    * ``X | Y`` e ``Optional[X]``: qualquer alternativa;
    * ``Literal[a, b]``: o valor tem de ser IGUAL a um deles (e do mesmo tipo:
      ``True`` não casa com ``Literal[1]``);
    * ``list[T]``, ``set[T]``, ``frozenset[T]``: o contêiner e todos os itens;
    * ``dict[K, V]``: chaves e valores;
    * ``tuple[X, Y]`` (tamanho fixo) e ``tuple[X, ...]`` (qualquer tamanho).
    """
    raise NotImplementedError


def check_call(func, *args, **kwargs):
    """Valida os argumentos de ``func(*args, **kwargs)`` contra as anotações
    (``typing.get_type_hints`` e ``inspect.signature(...).bind``), chama a função
    e valida o RETORNO. Parâmetros sem anotação não são verificados.

    Erros: ``TypeError(f"{nome}: {valor!r} não é {anotação}")`` para um argumento
    (``nome`` é o do parâmetro) e ``TypeError(f"retorno: {valor!r} não é
    {anotação}")`` para o retorno. Devolve o resultado da função."""
    raise NotImplementedError
