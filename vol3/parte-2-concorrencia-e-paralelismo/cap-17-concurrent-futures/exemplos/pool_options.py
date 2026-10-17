"""initializer, max_tasks_per_child, mp_context e falhas de processos."""
import concurrent.futures as cf
import multiprocessing as mp

import tasks

STATE = {}


def init_worker(label):
    STATE["label"] = label


def read_state(_):
    return STATE.get("label")


if __name__ == "__main__":
    with cf.ProcessPoolExecutor(2, initializer=init_worker, initargs=("configurado",)) as pool:
        print("initializer rodou em cada filho:", set(pool.map(read_state, range(4))))

    with cf.ProcessPoolExecutor(2, max_tasks_per_child=2) as pool:
        pids = list(pool.map(tasks.pid, range(12), chunksize=1))
    print("max_tasks_per_child=2: PIDs distintos em 12 tarefas =", len(set(pids)), "(cada filho vive só 2 tarefas: bom contra vazamento de memória)")

    with cf.ProcessPoolExecutor(2, mp_context=mp.get_context("spawn")) as pool:
        print("mp_context explícito:", list(pool.map(tasks.square, range(4))))

    with cf.ProcessPoolExecutor(2) as pool:
        future = pool.submit(tasks.crash)
        try:
            future.result()
        except cf.BrokenExecutor as error:
            print("filho morreu ->", type(error).__name__)
            print("  causa (3.15):", str(error.__cause__).strip().replace("\n", " "))
        try:
            pool.submit(tasks.square, 1)
        except cf.BrokenExecutor:
            print("o executor inteiro fica QUEBRADO: submit() depois também levanta BrokenExecutor")
