"""Exercício 3: a ``Store``: o "controlador" mínimo do estilo Elm, com desfazer, refazer e viagem no tempo de graça."""


class Store:
    """``Store(update, state, limit=None)``: ``update(state, msg)`` devolve o estado novo (função pura; os estados são imutáveis e comparáveis com ``==``).

    * ``state``: o estado atual (atributo);
    * ``dispatch(msg)``: calcula ``novo = update(state, msg)``. Se ``novo == state``: NADA acontece (nenhum aviso, nenhum passo no histórico) e devolve ``False``. Senão guarda o estado
      antigo no passado, APAGA o futuro (refazer), passa a ser ``novo``, avisa os assinantes (com o estado novo) e devolve ``True``. Se ``update`` levantar uma exceção, nada muda
      (nem o estado, nem o histórico, nem os avisos) e a exceção continua subindo;
    * ``limit``: o máximo de estados que o PASSADO guarda (os mais antigos são esquecidos); ``limit < 1``: ``ValueError("limite inválido")`` (``None`` é sem limite);
    * ``subscribe(fn)``: ``fn(state)`` é chamada a cada mudança de estado (também por ``undo``, ``redo`` e ``jump``), na ORDEM de inscrição; devolve uma função ``unsubscribe()`` que tira
      ``fn`` (chamar de novo não faz mal). Uma ``fn`` pode se desinscrever DURANTE um aviso sem atrapalhar os outros assinantes daquele aviso;
    * ``undo()`` e ``redo()``: devolvem ``True`` se andaram, ``False`` se não havia para onde; avisam os assinantes;
    * ``can_undo`` e ``can_redo`` (propriedades);
    * ``timeline()``: a lista de TODOS os estados em ordem cronológica (o passado, o atual e o futuro); ``position`` (propriedade): o índice do estado atual em ``timeline()``;
    * ``jump(index)``: vai para o estado ``index`` da linha do tempo (avisa UMA vez, e só se mudou de posição); fora de ``0..len-1``: ``IndexError(f"posição inexistente: {index}")``."""

    def __init__(self, update, state, limit: int | None = None):
        raise NotImplementedError

    def dispatch(self, msg) -> bool:
        raise NotImplementedError

    def subscribe(self, fn):
        raise NotImplementedError

    def undo(self) -> bool:
        raise NotImplementedError

    def redo(self) -> bool:
        raise NotImplementedError

    @property
    def can_undo(self) -> bool:
        raise NotImplementedError

    @property
    def can_redo(self) -> bool:
        raise NotImplementedError

    def timeline(self) -> list:
        raise NotImplementedError

    @property
    def position(self) -> int:
        raise NotImplementedError

    def jump(self, index: int) -> None:
        raise NotImplementedError
