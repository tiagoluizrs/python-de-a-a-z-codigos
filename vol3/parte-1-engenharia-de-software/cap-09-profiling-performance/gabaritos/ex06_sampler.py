"""Gabarito do exercício 6."""
import sys
import threading
from collections import Counter


def sample_profile(func, *args, interval=0.001, **kwargs):
    main_id = threading.get_ident()
    counter = Counter()
    stop = threading.Event()

    def sampler():
        while not stop.wait(interval):
            frame = sys._current_frames().get(main_id)
            if frame is not None:
                counter[frame.f_code.co_name] += 1

    thread = threading.Thread(target=sampler, daemon=True)
    thread.start()
    try:
        result = func(*args, **kwargs)
    finally:
        stop.set()
        thread.join()
    return result, counter


def hottest(counter, n=1):
    total = sum(counter.values())
    if not total:
        return []
    return [(name, count / total) for name, count in counter.most_common(n)]
