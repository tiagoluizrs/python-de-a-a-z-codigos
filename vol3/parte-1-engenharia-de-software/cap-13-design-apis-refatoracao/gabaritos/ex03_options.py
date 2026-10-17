"""Gabarito do exercício 3."""
from dataclasses import dataclass, fields, replace

METHODS = {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD"}


def request_legacy(url, method="GET", timeout=10.0, retries=3, verify=True, headers=None, proxy=None, follow=True):
    return (url, method, timeout, retries, verify, tuple((headers or {}).items()), proxy, follow)


@dataclass(frozen=True)
class Options:
    method: str = "GET"
    timeout: float = 10.0
    retries: int = 3
    verify: bool = True
    headers: tuple = ()
    proxy: str | None = None
    follow: bool = True

    def __post_init__(self):
        method = self.method.upper()
        if method not in METHODS:
            raise ValueError(f"method inválido: {self.method!r}")
        object.__setattr__(self, "method", method)
        if self.timeout <= 0:
            raise ValueError("timeout deve ser > 0")
        if self.retries < 0:
            raise ValueError("retries deve ser >= 0")

    def with_(self, **changes):
        known = {f.name for f in fields(self)}
        for name in changes:
            if name not in known:
                raise TypeError(f"opção desconhecida: {name!r}")
        return replace(self, **changes)

    @classmethod
    def from_legacy(cls, **kwargs):
        headers = kwargs.pop("headers", None)
        if headers is not None:
            kwargs["headers"] = tuple(headers.items())
        return cls(**kwargs)


def request(url, *, options=None, **overrides):
    final = (options or Options()).with_(**overrides)
    return url, final
