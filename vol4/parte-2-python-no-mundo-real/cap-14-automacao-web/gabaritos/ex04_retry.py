"""Gabarito do exercício 4."""


class GaveUp(Exception):
    pass


def get_with_backoff(get, url, sleep, max_attempts=4, base=0.5, cap=8.0):
    status = None
    for attempt in range(max_attempts):
        status, headers, body = get(url)
        if status < 500 and status != 429:
            return body
        if attempt == max_attempts - 1:
            break
        retry_after = headers.get("retry-after")
        wait = float(retry_after) if retry_after and retry_after.replace(".", "", 1).isdigit() else min(base * 2 ** attempt, cap)
        sleep(wait)
    raise GaveUp(f"desistindo de {url} após {max_attempts} tentativas (último status: {status})")
