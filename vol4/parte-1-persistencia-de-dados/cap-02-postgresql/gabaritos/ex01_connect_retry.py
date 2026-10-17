"""Gabarito do exercício 1."""
import time

import psycopg


def connect_with_retry(connect, attempts=5, delay=0.1, max_delay=2.0, sleep=time.sleep):
    if attempts < 1:
        raise ValueError("attempts >= 1")
    wait = delay
    for attempt in range(1, attempts + 1):
        try:
            return connect()
        except psycopg.OperationalError:
            if attempt == attempts:
                raise
            sleep(min(wait, max_delay))
            wait *= 2
