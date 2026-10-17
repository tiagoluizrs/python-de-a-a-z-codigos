"""Exercício 4: um pool de threads mínimo (sem concurrent.futures)."""


class Handle:
    """Resultado futuro de uma tarefa: ``result(timeout=None)`` espera e devolve o
    valor, ou re-levanta a exceção que a tarefa levantou; ``TimeoutError`` se
    passar do tempo; ``done()`` diz se terminou."""


class WorkerPool:
    """``WorkerPool(workers)`` inicia ``workers`` threads.

    * ``submit(func, *args, **kwargs)`` -> ``Handle`` (tarefas executadas na ORDEM
      de submissão, por qualquer worker livre);
    * as exceções das tarefas são CAPTURADAS e entregues por ``Handle.result()``;
      a thread do worker continua viva;
    * ``shutdown(wait=True)``: não aceita mais tarefas (``submit`` depois levanta
      ``RuntimeError``), deixa terminar as que já estão na fila e, com ``wait``,
      espera as threads;
    * ``len(pool.threads)`` é o número de workers; use uma ``queue.Queue`` e uma
      sentinela por worker; threads com ``name="pool-<i>"``;
    * funciona como gerenciador de contexto (``__exit__`` faz ``shutdown(wait=True)``)."""

    def __init__(self, workers):
        raise NotImplementedError
