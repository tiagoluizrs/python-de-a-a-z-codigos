"""Exercício 4: uma fila que não perde trabalho quando o trabalhador morre."""


class ReliableQueue:
    """``ReliableQueue(redis, name)`` com ``redis`` criado com ``decode_responses=True``.

    * ``put(item)``: ``RPUSH`` em ``q:<name>``; devolve o tamanho da fila;
    * ``get(worker, timeout=1)``: move atomicamente o PRIMEIRO item da fila para a lista
      ``q:<name>:processing:<worker>`` (``BLMOVE`` ``LEFT``/``RIGHT``, com ``timeout`` segundos de
      espera) e o devolve; fila vazia depois do prazo devolve ``None``;
    * ``ack(worker, item)``: remove UMA ocorrência do item da lista de processamento do trabalhador;
      ``True`` se removeu;
    * ``recover(worker)``: devolve TODOS os itens em processamento do trabalhador para o INÍCIO da
      fila, preservando a ordem original em que foram retirados; devolve quantos voltaram;
    * ``pending(worker)`` -> lista dos itens em processamento; ``size()`` -> tamanho da fila."""

    def __init__(self, redis, name):
        raise NotImplementedError
