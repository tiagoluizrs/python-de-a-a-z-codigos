"""Gabarito do exercício 3."""


def _check_timeout(timeout):
    if timeout <= 0:
        raise ValueError("timeout inválido")


def _check_retries(retries):
    if retries < 0:
        raise ValueError("retries inválido")


class Fetcher:
    def __init__(self, transport, *, timeout=5.0, headers=None, retries=0):
        _check_timeout(timeout)
        _check_retries(retries)
        self.transport = transport
        self._timeout, self._headers, self._retries = timeout, dict(headers or {}), retries
        self._calls = 0
        self._extra = 0

    def get(self, url, *, timeout=None, headers=None, retries=None):
        timeout = self._timeout if timeout is None else timeout
        retries = self._retries if retries is None else retries
        _check_timeout(timeout)
        _check_retries(retries)
        merged = {**self._headers, **(headers or {})}
        self._calls += 1
        attempt = 0
        while True:
            try:
                return self.transport.request(url, timeout, merged)
            except ConnectionError:
                if attempt >= retries:
                    raise
                attempt += 1
                self._extra += 1

    def with_options(self, **changes):
        for name in changes:
            if name not in ("timeout", "headers", "retries"):
                raise TypeError(f"opção desconhecida: {name}")
        return Fetcher(
            self.transport,
            timeout=changes.get("timeout", self._timeout),
            headers={**self._headers, **changes.get("headers", {})},
            retries=changes.get("retries", self._retries),
        )

    @property
    def stats(self):
        return {"calls": self._calls, "retries": self._extra}
