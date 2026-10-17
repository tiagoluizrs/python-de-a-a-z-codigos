"""Gabarito do exercício 4."""
import time


def submit_with_retry(executor, func, *args, retries=3, retry_on=(Exception,), delay=0.0, sleep=time.sleep):
    if retries < 0:
        raise ValueError("retries >= 0")
    attempt = 0
    while True:
        future = executor.submit(func, *args)
        try:
            return future.result()
        except retry_on:
            if attempt >= retries:
                raise
            if delay:
                sleep(delay * 2**attempt)
            attempt += 1
