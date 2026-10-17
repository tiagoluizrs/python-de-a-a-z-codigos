"""Gabarito do exercício 1."""
import json
from dataclasses import dataclass
from urllib.parse import urlencode


@dataclass(frozen=True)
class Request:
    method: str
    url: str
    headers: tuple
    params: tuple
    body: str | None = None

    @property
    def full_url(self):
        if not self.params:
            return self.url
        return self.url + ("&" if "?" in self.url else "?") + urlencode(self.params)


class RequestBuilder:
    def __init__(self):
        self._method = "GET"
        self._url = None
        self._headers = []
        self._params = []
        self._body = None

    def method(self, m):
        m = m.upper()
        if m not in ("GET", "POST", "PUT", "DELETE"):
            raise ValueError(f"método inválido: {m}")
        self._method = m
        return self

    def url(self, u):
        self._url = u
        return self

    def header(self, name, value):
        self._headers.append((name, value))
        return self

    def param(self, name, value):
        self._params.append((name, str(value)))
        return self

    def json_body(self, obj):
        self._body = json.dumps(obj)
        self._headers.append(("Content-Type", "application/json"))
        return self

    def build(self):
        if self._url is None:
            raise ValueError("url obrigatória")
        if self._body is not None and self._method in ("GET", "DELETE"):
            raise ValueError(f"{self._method} não aceita corpo")
        return Request(self._method, self._url, tuple(self._headers), tuple(self._params), self._body)
