"""Exercício 4: uma torre de controle: o mediador que decide quem pousa (as regras de coordenação em um só lugar)."""


class Plane:
    """(Pronto, NÃO edite.) Um colega: tem ``name`` e uma lista ``messages`` com o que a torre lhe disse via ``notify``."""

    def __init__(self, name: str):
        self.name, self.messages = name, []

    def notify(self, message: str) -> None:
        self.messages.append(message)


class Tower:
    """Uma pista, uma fila. Os aviões só falam com a torre.

    * ``request_landing(plane, emergency=False)``: pista livre: o avião ocupa a pista, recebe ``"pouso autorizado"`` e a função devolve ``0``. Pista ocupada: entra na fila e recebe
      ``f"na fila: posição {n}"`` (``n`` a partir de 1), e a função devolve ``n``. A ORDEM da fila: todas as EMERGÊNCIAS primeiro (entre elas, por ordem de chegada), depois os normais (por ordem de chegada);
      uma emergência que chega passa na frente dos normais mas NÃO na frente de outra emergência que já estava; quando a fila muda por causa de uma emergência, os normais afetados recebem a nova
      posição (``f"na fila: posição {n}"``). O mesmo avião pedindo de novo (já na pista ou na fila): ``ValueError(f"{plane.name} já está no sistema")``;
    * ``landed(plane)``: o avião precisa ser o que está na pista (``ValueError(f"{plane.name} não está na pista")``); libera a pista, o PRÓXIMO da fila (se houver) ocupa a pista e recebe
      ``"pouso autorizado"``; os que continuam na fila recebem a nova posição; devolve o avião que passou a ocupar a pista (ou ``None``);
    * ``cancel(plane)``: retira da fila (os que ficam atrás recebem a nova posição); avião na pista: ``ValueError("avião na pista não pode cancelar")``; avião fora do sistema:
      ``LookupError(f"{plane.name} não está na fila")``;
    * ``runway``: o avião na pista (ou ``None``); ``waiting()``: os nomes na fila, na ordem; ``len(tower)``: quantos aviões estão no sistema (pista + fila).
    Uma notificação de posição só é enviada quando a posição REALMENTE mudou."""

    def __init__(self):
        raise NotImplementedError

    def request_landing(self, plane: Plane, emergency: bool = False) -> int:
        raise NotImplementedError

    def landed(self, plane: Plane):
        raise NotImplementedError

    def cancel(self, plane: Plane) -> None:
        raise NotImplementedError

    @property
    def runway(self):
        raise NotImplementedError

    def waiting(self) -> list[str]:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError
