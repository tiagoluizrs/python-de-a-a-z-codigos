"""Gabarito do exercício 3."""
import concurrent.futures as cf


def map_with_progress(executor, func, items, on_progress=None):
    items = list(items)
    if not items:
        return []
    futures = {executor.submit(func, item): index for index, item in enumerate(items)}
    results = [None] * len(items)
    done = 0
    for future in cf.as_completed(futures):
        try:
            results[futures[future]] = future.result()
        except BaseException:
            for other in futures:
                other.cancel()
            raise
        done += 1
        if on_progress:
            on_progress(done, len(items))
    return results
