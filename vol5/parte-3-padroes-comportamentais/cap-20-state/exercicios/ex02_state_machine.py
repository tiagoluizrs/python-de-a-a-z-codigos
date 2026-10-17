"""Exercício 2: uma máquina de estados GENÉRICA, guiada por uma tabela de transições (dados, não classes)."""
from collections import deque


class InvalidTransition(Exception):
    pass


class StateMachine:
    """``StateMachine(table, initial)``: ``table`` é um dict ``{(estado, evento): próximo_estado}`` (estados e eventos podem ser textos ou Enums).

    * ``initial`` precisa aparecer na tabela como estado de origem OU de destino: senão ``ValueError(f"estado inicial desconhecido: {initial!r}")``;
    * ``state``: o estado atual; ``history``: a lista (cópia) dos estados por onde passou, começando pelo inicial;
    * ``fire(event)``: aplica a transição e devolve o NOVO estado; evento sem transição no estado atual:
      ``InvalidTransition(f"{event} não permitido em {estado}")`` (para Enums, use ``.value`` se o estado tiver esse atributo; senão ``str(estado)``) e nada muda;
    * ``can(event)``: ``True`` se há transição para o evento no estado atual; ``allowed()``: a lista ORDENADA (``sorted`` por ``str``) dos eventos aceitos agora;
    * ``is_terminal``: verdadeiro se NENHUM evento sai do estado atual;
    * ``on_transition(callback)``: registra ``callback(origem, evento, destino)`` chamado DEPOIS de cada transição bem-sucedida, na ordem do registro; devolve o ``callback``;
    * ``reset()``: volta ao estado inicial e zera a história."""

    def __init__(self, table: dict, initial):
        raise NotImplementedError

    @property
    def state(self):
        raise NotImplementedError

    @property
    def history(self) -> list:
        raise NotImplementedError

    def fire(self, event):
        raise NotImplementedError

    def can(self, event) -> bool:
        raise NotImplementedError

    def allowed(self) -> list:
        raise NotImplementedError

    @property
    def is_terminal(self) -> bool:
        raise NotImplementedError

    def on_transition(self, callback):
        raise NotImplementedError

    def reset(self) -> None:
        raise NotImplementedError


def validate_table(table: dict, initial) -> dict:
    """Analisa o grafo da tabela a partir de ``initial`` e devolve ``{"unreachable": [...], "terminal": [...], "dead_events": [...]}``, cada lista ORDENADA por ``str``:

    * ``unreachable``: estados (de origem ou de destino) que NÃO podem ser alcançados a partir de ``initial`` (busca em largura);
    * ``terminal``: estados de onde NENHUM evento sai (são o fim legítimo do fluxo; só informação);
    * ``dead_events``: eventos que só aparecem em transições cuja origem é inalcançável (nunca poderão ser disparados)."""
    raise NotImplementedError


def shortest_path(table: dict, start, goal) -> list | None:
    """O caminho MAIS CURTO de EVENTOS de ``start`` até ``goal`` (``list``), por busca em largura, visitando os eventos de cada estado em ordem alfabética (``str``);
    ``[]`` se ``start == goal``; ``None`` se não há caminho."""
    raise NotImplementedError
