"""Exercício 2: uma fila CONFIÁVEL em memória (a mesma semântica da fila de Redis do capítulo), com relógio injetado."""


class FakeClock:
    def __init__(self, now: float = 0.0):
        self.now = now

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


class ReliableQueue:
    """Entrega "pelo menos uma vez" com confirmação, prazo de visibilidade, novas tentativas e fila de mortas.

    * ``ReliableQueue(clock, visibility=30.0, max_attempts=3, retry_delay=lambda attempts: 1.0)``: ``clock()`` devolve o
      "agora" (segundos); ``retry_delay(tentativas)`` dá a espera antes de uma nova tentativa;
    * ``put(payload, delay=0.0) -> str``: enfileira (ids ``"m1"``, ``"m2"``... na ordem); com ``delay``, a mensagem só
      fica disponível a partir de ``agora + delay``;
    * ``get() -> tuple[str, object] | None``: devolve ``(id, payload)`` da mensagem DISPONÍVEL mais antiga (FIFO por ordem de
      ``put``; as adiadas só entram quando chegar a hora) e a marca "em processamento" com prazo ``agora + visibility``;
      ``None`` se não houver nada disponível;
    * ``ack(id)``: a mensagem termina de vez (``KeyError`` se ela não estiver em processamento);
    * ``nack(id) -> float | None``: falhou. Conta uma tentativa; se as tentativas chegarem a ``max_attempts``, vai para a fila
      de mortas (``dead``, lista de ids) e devolve ``None``; senão volta a ficar disponível depois de
      ``retry_delay(tentativas)`` e devolve essa espera. ``KeyError`` se não estiver em processamento;
    * ``reap() -> int``: toda mensagem em processamento cujo prazo VENCEU (``prazo <= agora``) volta a ficar disponível
      imediatamente, contando como uma tentativa (se isso esgotar ``max_attempts``, vai para ``dead``); devolve quantas
      foram tratadas;
    * ``attempts(id) -> int``: tentativas contadas até agora;
    * ``sizes() -> dict``: ``{"ready": n, "inflight": n, "delayed": n, "dead": n}`` (``ready`` = disponíveis agora;
      ``delayed`` = as que ainda esperam a hora)."""

    def __init__(self, clock, visibility: float = 30.0, max_attempts: int = 3, retry_delay=lambda attempts: 1.0):
        raise NotImplementedError

    def put(self, payload, delay: float = 0.0) -> str:
        raise NotImplementedError

    def get(self):
        raise NotImplementedError

    def ack(self, msg_id: str) -> None:
        raise NotImplementedError

    def nack(self, msg_id: str):
        raise NotImplementedError

    def reap(self) -> int:
        raise NotImplementedError

    def attempts(self, msg_id: str) -> int:
        raise NotImplementedError

    def sizes(self) -> dict:
        raise NotImplementedError

    @property
    def dead(self) -> list:
        raise NotImplementedError
