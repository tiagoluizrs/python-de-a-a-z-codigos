"""submit, map, Future, as_completed, wait."""
import concurrent.futures as cf
import os
import time

import tasks

if __name__ == "__main__":
    print("max_workers padrão: ThreadPoolExecutor =", cf.ThreadPoolExecutor()._max_workers, "| ProcessPoolExecutor =", cf.ProcessPoolExecutor()._max_workers, "| process_cpu_count =", os.process_cpu_count())

    with cf.ThreadPoolExecutor(max_workers=4) as pool:
        # map: resultados NA ORDEM de entrada
        print("map            :", list(pool.map(tasks.square, range(6))))

        # submit: devolve um Future imediatamente
        future = pool.submit(tasks.slow, 0.2)
        print("recém-criado   : done =", future.done(), "| running =", future.running())
        print("result()       :", future.result(), "| done =", future.done())

        # as_completed: na ORDEM DE TÉRMINO
        futures = {pool.submit(tasks.slow, s): s for s in (0.3, 0.1, 0.2)}
        print("as_completed   :", [futures[f] for f in cf.as_completed(futures)], "(pedidos 0.3, 0.1, 0.2)")

        # wait: com return_when
        pair = [pool.submit(tasks.slow, 0.05), pool.submit(tasks.slow, 0.5)]
        done, not_done = cf.wait(pair, timeout=0.3, return_when=cf.FIRST_COMPLETED)
        print(f"wait(FIRST_COMPLETED): {len(done)} pronto, {len(not_done)} pendente")

        # exceções: ficam guardadas no Future
        bad = pool.submit(tasks.fail, 2)
        print("exception()    :", repr(bad.exception()), "| result() levanta:", end=" ")
        try:
            bad.result()
        except ValueError as error:
            print("ValueError:", error)

        # map só levanta ao ITERAR até o item que falhou
        results = pool.map(tasks.fail, range(5))
        print("map devolveu um iterador; erro só ao consumir:", end=" ")
        try:
            list(results)
        except ValueError as error:
            print(error)

        # timeout em result(): TimeoutError, mas a tarefa continua
        slow = pool.submit(tasks.slow, 0.4)
        try:
            slow.result(timeout=0.05)
        except TimeoutError:
            print("result(timeout) -> TimeoutError (é o TimeoutError embutido); a tarefa segue: done =", slow.done())

        # callbacks
        seen = []
        callback_future = pool.submit(tasks.square, 7)
        callback_future.add_done_callback(lambda f: seen.append(f.result()))
        callback_future.result()
        time.sleep(0.05)
        print("add_done_callback:", seen)
