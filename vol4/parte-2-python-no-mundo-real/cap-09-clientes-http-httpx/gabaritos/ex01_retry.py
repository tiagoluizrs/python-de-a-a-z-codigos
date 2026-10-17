"""Gabarito do exercício 1."""
import time

import httpx

IDEMPOTENT = {"GET", "HEAD", "PUT", "DELETE", "OPTIONS"}


def request_with_retry(client, method, url, *, retries=3, backoff=0.1, retry_statuses=(429, 502, 503, 504), sleep=time.sleep, **kwargs):
    if retries < 0:
        raise ValueError("retries >= 0")
    safe = method.upper() in IDEMPOTENT
    response = None
    for attempt in range(1, retries + 2):
        try:
            response = client.request(method, url, **kwargs)
            error = None
        except (httpx.ConnectError, httpx.ReadTimeout) as exc:
            if not safe:
                raise
            response, error = None, exc
        retryable = error is not None or response.status_code in retry_statuses
        if not (safe and retryable) or attempt == retries + 1:
            if error is not None:
                raise error
            return response
        wait = backoff * 2 ** (attempt - 1)
        if response is not None and "retry-after" in response.headers:
            wait = float(response.headers["retry-after"])
        sleep(wait)
    raise AssertionError("inalcançável")
