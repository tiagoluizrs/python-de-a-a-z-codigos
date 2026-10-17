"""Gabarito do exercício 5."""
import concurrent.futures as cf


def bounded_map(executor, func, items, max_pending=8):
    if max_pending < 1:
        raise ValueError("max_pending >= 1")
    pending = {}
    results = {}
    count = 0
    try:
        for item in items:
            while len(pending) >= max_pending:
                done, _ = cf.wait(pending, return_when=cf.FIRST_COMPLETED)
                for future in done:
                    results[pending.pop(future)] = future.result()
            pending[executor.submit(func, item)] = count
            count += 1
        for future in cf.as_completed(list(pending)):
            results[pending.pop(future)] = future.result()
    except BaseException:
        for future in pending:
            future.cancel()
        raise
    return [results[i] for i in range(count)]
