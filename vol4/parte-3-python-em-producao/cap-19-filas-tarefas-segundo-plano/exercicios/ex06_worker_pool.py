"""Exercício 6: um pool de workers com fila limitada, novas tentativas e encerramento limpo (threads)."""


def run_workers(tasks: list, handler, concurrency: int = 4, max_attempts: int = 3, queue_size: int = 10) -> dict:
    """Processa ``tasks`` (uma lista de itens quaisquer) com ``concurrency`` threads trabalhadoras.

    * a fila entre quem enfileira e os workers tem TAMANHO MÁXIMO ``queue_size`` (``queue.Queue(maxsize=...)``): enfileirar
      bloqueia quando está cheia (contrapressão);
    * cada worker chama ``handler(item)``; se levantar exceção, o item é tentado de novo (na mesma fila, no fim) até
      ``max_attempts`` tentativas TOTAIS; esgotadas, o item vai para ``failed`` com o último erro;
    * a ordem de processamento não é garantida, mas CADA item é processado até ter sucesso ou esgotar as tentativas;
    * ao final, todos os workers devem ter TERMINADO (sem threads penduradas; use sentinelas ``None`` e ``join``);
    * devolva ``{"ok": [resultados na ORDEM de ``tasks``, apenas dos que deram certo], "failed": [(item, erro), ...] na ordem de
      ``tasks``, "attempts": {indice_do_item: tentativas feitas}}``.

    ``concurrency < 1`` ou ``max_attempts < 1``: ``ValueError``. ``tasks`` vazia: ``{"ok": [], "failed": [], "attempts": {}}``.

    Dica: guarde ``(indice, item, tentativa)`` na fila; para repor um item que falhou sem bloquear o próprio worker (a fila pode
    estar cheia), use uma segunda fila SEM limite apenas para os reenvios, ou ``put_nowait`` com um deque de espera."""
    raise NotImplementedError
