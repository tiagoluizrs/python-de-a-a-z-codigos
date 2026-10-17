"""Exercício 3: comandos SEM classes: pares ``(fazer, desfazer)`` de funções, uma pilha de desfazer e uma fila de ações."""


def make_set(store: dict, key, value):
    """Devolve ``(do, undo)``: ``do()`` grava ``store[key] = value`` (guardando o valor antigo, ou a ausência, em uma closure); ``undo()`` restaura. ``undo`` antes
    de ``do``: ``RuntimeError("comando não executado")``."""
    raise NotImplementedError


def make_append(items: list, item):
    """Devolve ``(do, undo)``: ``do()`` faz ``items.append(item)``; ``undo()`` remove ESSE acréscimo (o último elemento deve ser o ``item`` acrescentado, senão
    ``RuntimeError("lista alterada por fora")``)."""
    raise NotImplementedError


def make_increment(counters: dict, key, by: int = 1):
    """Devolve ``(do, undo)``: ``do()`` soma ``by`` a ``counters[key]`` (começando em 0 se a chave não existe) e ``undo()`` subtrai ``by`` (removendo a chave se ela não
    existia antes do ``do``). ``by == 0``: ``ValueError("incremento nulo")`` (na criação)."""
    raise NotImplementedError


class UndoStack:
    """Uma pilha de desfazer para pares ``(do, undo)``.

    * ``do(pair)``: chama ``pair[0]()`` e, se der certo, empilha o par; se levantar exceção, nada é empilhado e ela sobe;
    * ``undo()``: desfaz o último (``pair[1]()``) e o remove da pilha; devolve ``True``; pilha vazia: ``False``;
    * ``undo_all()``: desfaz TODOS, do mais recente ao mais antigo, e devolve quantos foram desfeitos; se um ``undo`` levantar exceção, os demais ainda são tentados e a
      PRIMEIRA exceção é levantada no fim (a pilha fica vazia);
    * ``commit()``: descarta a pilha SEM desfazer nada e devolve quantos pares havia;
    * ``len(stack)``.
    Também funciona como gerenciador de contexto: ao sair do ``with`` por uma EXCEÇÃO, faz ``undo_all()`` (e deixa a exceção original subir); ao sair normalmente, nada é
    desfeito (a pilha continua com o que tinha)."""

    def __init__(self):
        raise NotImplementedError

    def do(self, pair) -> None:
        raise NotImplementedError

    def undo(self) -> bool:
        raise NotImplementedError

    def undo_all(self) -> int:
        raise NotImplementedError

    def commit(self) -> int:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError

    def __enter__(self):
        raise NotImplementedError

    def __exit__(self, exc_type, exc, tb):
        raise NotImplementedError


class CommandQueue:
    """Guarda ações para executar DEPOIS. ``submit(fn, *args, **kwargs)`` guarda (``fn`` não chamável: ``TypeError``) e devolve a posição (0, 1, 2...); ``run_all()``
    executa todas em ordem FIFO, esvazia a fila e devolve a lista de resultados, na ordem; uma ação que levanta ``Exception`` NÃO interrompe as outras: no lugar do
    resultado fica a PRÓPRIA exceção (a instância). ``len(queue)`` e ``clear()`` (devolve quantas descartou)."""

    def __init__(self):
        raise NotImplementedError

    def submit(self, fn, *args, **kwargs) -> int:
        raise NotImplementedError

    def run_all(self) -> list:
        raise NotImplementedError

    def clear(self) -> int:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError
