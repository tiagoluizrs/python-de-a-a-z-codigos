"""Gabarito do exercício 5."""


def choose_arraysize(row_bytes, target_batch_bytes=1_000_000, minimum=10, maximum=10_000):
    if row_bytes <= 0 or minimum > maximum:
        raise ValueError("row_bytes > 0 e minimum <= maximum")
    return max(minimum, min(maximum, target_batch_bytes // row_bytes))


def fetch_in_batches(cursor, size):
    if size < 1:
        raise ValueError("size >= 1")
    while batch := cursor.fetchmany(size):
        yield batch
