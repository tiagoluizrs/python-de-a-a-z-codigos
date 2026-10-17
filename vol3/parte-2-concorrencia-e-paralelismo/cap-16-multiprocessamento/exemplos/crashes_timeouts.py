"""Quando o filho falha: morte brusca, travamento e o relatório do 3.15."""
import concurrent.futures as cf
import multiprocessing as mp

import tasks

if __name__ == "__main__":
    p = mp.Process(target=tasks.crash)
    p.start()
    p.join()
    print("filho morreu com os._exit(7): exitcode =", p.exitcode, "(no Unix, negativo = número do sinal)")

    with cf.ProcessPoolExecutor(2) as pool:
        try:
            pool.submit(tasks.crash).result()
        except cf.process.BrokenProcessPool as error:
            print("ProcessPoolExecutor:", type(error).__name__)
            print("  causa no 3.15 (PID e exit code):", str(error.__cause__).strip().replace("\n", " "))

    p = mp.Process(target=tasks.slow, args=(30,))
    p.start()
    p.join(timeout=0.3)
    print("depois de join(0.3): is_alive =", p.is_alive())
    p.terminate()                                   # força: o filho NÃO faz limpeza
    p.join()
    print("depois de terminate(): exitcode =", p.exitcode)

    with mp.Pool(2) as pool:
        result = pool.apply_async(tasks.slow, (30,))
        try:
            result.get(timeout=0.3)
        except mp.TimeoutError:
            print("AsyncResult.get(timeout) -> TimeoutError; a tarefa CONTINUA rodando (o with do Pool a termina)")
