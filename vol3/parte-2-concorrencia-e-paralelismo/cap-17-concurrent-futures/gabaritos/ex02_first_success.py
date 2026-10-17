"""Gabarito do exercício 2."""
import concurrent.futures as cf


def first_success(funcs, workers=None):
    funcs = list(funcs)
    if not funcs:
        raise ValueError("funcs vazio")
    pool = cf.ThreadPoolExecutor(max_workers=workers or len(funcs))
    errors = []
    try:
        pending = {pool.submit(func) for func in funcs}
        while pending:
            done, pending = cf.wait(pending, return_when=cf.FIRST_COMPLETED)
            for future in done:
                error = future.exception()
                if error is None:
                    for other in pending:
                        other.cancel()
                    return future.result()
                errors.append(error)
        raise RuntimeError("todos falharam", errors)
    finally:
        pool.shutdown(wait=False, cancel_futures=True)
