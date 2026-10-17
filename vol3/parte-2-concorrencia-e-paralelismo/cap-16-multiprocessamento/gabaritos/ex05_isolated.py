"""Gabarito do exercício 5."""
import multiprocessing as mp
import queue

import tasks


class ProcessCrashed(Exception):
    def __init__(self, exitcode):
        super().__init__(f"processo terminou com exitcode {exitcode}")
        self.exitcode = exitcode


def run_isolated(func, *args, timeout=None):
    ctx = mp.get_context("spawn")
    out = ctx.Queue()
    process = ctx.Process(target=tasks.child_main, args=(out, func, args))
    process.start()
    try:
        try:
            kind, payload = out.get(timeout=timeout)
        except queue.Empty:
            process.join(0.2)
            if process.is_alive():
                process.terminate()
                process.join()
                raise TimeoutError(f"passou de {timeout} s") from None
            raise ProcessCrashed(process.exitcode) from None
        process.join()
        if kind == "error":
            raise payload
        return payload
    finally:
        if process.is_alive():
            process.terminate()
            process.join()
