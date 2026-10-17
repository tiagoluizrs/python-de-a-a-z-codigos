"""Cancelar Futures, shutdown(cancel_futures) e o que NÃO se cancela."""
import concurrent.futures as cf

import tasks

if __name__ == "__main__":
    with cf.ThreadPoolExecutor(max_workers=1) as pool:
        running = pool.submit(tasks.slow, 0.3)
        pending = pool.submit(tasks.slow, 0.1)
        print("cancel() de tarefa EM EXECUÇÃO :", running.cancel())
        print("cancel() de tarefa na fila      :", pending.cancel(), "| cancelled =", pending.cancelled())
        try:
            pending.result()
        except cf.CancelledError:
            print("result() de cancelada levanta CancelledError")

    with cf.ThreadPoolExecutor(max_workers=1) as pool:
        first = pool.submit(tasks.slow, 0.3)
        queued = [pool.submit(tasks.slow, 0.1) for _ in range(5)]
        pool.shutdown(wait=True, cancel_futures=True)
        print("shutdown(cancel_futures=True): canceladas =", sum(f.cancelled() for f in queued), "de 5; a que já rodava terminou:", first.result())

    pool = cf.ThreadPoolExecutor(max_workers=1)
    pool.shutdown()
    try:
        pool.submit(tasks.square, 1)
    except RuntimeError as error:
        print("submit depois do shutdown:", error)
