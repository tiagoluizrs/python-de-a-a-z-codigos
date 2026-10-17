"""Exercício 4: descritores: o "proxy de um atributo" (preguiçoso e validado), a ferramenta de Python por baixo de ``property`` e ``cached_property``."""


class lazy:
    """Descritor SEM dados (só ``__get__``) para uso como decorador de um método sem argumentos:

    * na PRIMEIRA leitura em uma instância, chama ``fn(instancia)`` e guarda o resultado em ``instancia.__dict__[nome]`` (o ``nome`` vem de ``__set_name__``);
      as leituras seguintes acham o valor no ``__dict__`` e nem chegam ao descritor;
    * lido pela CLASSE (``instancia is None``), devolve o próprio descritor;
    * como é um descritor sem ``__set__``, atribuir ``obj.nome = valor`` substitui o valor guardado, e ``del obj.nome`` o apaga (a próxima leitura recalcula);
    * uma exceção em ``fn`` sobe e nada é guardado."""

    def __init__(self, fn):
        raise NotImplementedError

    def __set_name__(self, owner, name):
        raise NotImplementedError

    def __get__(self, obj, owner=None):
        raise NotImplementedError


def reset_lazy(instance, name: str) -> bool:
    """Apaga o valor guardado por um ``lazy`` em ``instance.__dict__[name]``; devolve ``True`` se havia, ``False`` se não."""
    raise NotImplementedError


class Bounded:
    """Descritor COM dados (``__get__``, ``__set__`` e ``__delete__``) para atributos numéricos: ``Bounded(minimum=None, maximum=None, kind=(int, float))``.

    * ``__set_name__`` guarda o nome; o valor fica em ``instancia.__dict__["_" + nome]``;
    * ``__set__``: o valor precisa ser de um dos tipos de ``kind`` E NÃO pode ser ``bool`` (``True`` é um ``int`` em Python, mas aqui é um erro):
      senão ``TypeError(f"{nome} deve ser numérico")``; fora de ``[minimum, maximum]`` (limites inclusivos, ``None`` = sem limite):
      ``ValueError(f"{nome} fora do intervalo [{minimum}, {maximum}]")`` (com ``None`` escrito como está);
    * ``__get__``: pela classe devolve o descritor; pela instância devolve o valor; se nunca foi atribuído: ``AttributeError(f"{nome} não foi definido")``;
    * ``__delete__``: ``AttributeError(f"{nome} não pode ser apagado")``."""

    def __init__(self, minimum=None, maximum=None, kind=(int, float)):
        raise NotImplementedError

    def __set_name__(self, owner, name):
        raise NotImplementedError

    def __get__(self, obj, owner=None):
        raise NotImplementedError

    def __set__(self, obj, value):
        raise NotImplementedError

    def __delete__(self, obj):
        raise NotImplementedError
