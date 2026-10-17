"""Exercício 2: um buffer limitado com Condition (sem usar queue.Queue)."""
import queue  # noqa: F401  (apenas para as exceções queue.Full e queue.Empty)


class Closed(Exception):
    """O buffer foi fechado e está vazio."""


class BoundedBuffer:
    """Fila FIFO com capacidade fixa, para vários produtores e consumidores.

    * ``BoundedBuffer(capacity)`` (``capacity < 1`` levanta ``ValueError``);
    * ``put(item, timeout=None)``: espera haver espaço; com ``timeout`` (segundos)
      levanta ``queue.Full`` se não houver; em buffer FECHADO levanta ``Closed``;
    * ``get(timeout=None)``: espera haver item; com ``timeout`` levanta
      ``queue.Empty``; se o buffer foi fechado E está vazio, levanta ``Closed``
      (itens que ainda estão no buffer são entregues antes);
    * ``close()``: impede novos ``put`` e ACORDA quem espera;
    * ``len(buffer)``: itens atuais.
    Use UMA ``threading.Condition`` e ``wait_for`` com predicado."""

    def __init__(self, capacity):
        raise NotImplementedError
