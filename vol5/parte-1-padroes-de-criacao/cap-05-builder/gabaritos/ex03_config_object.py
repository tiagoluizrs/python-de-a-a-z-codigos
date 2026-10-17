"""Gabarito do exercício 3."""
import dataclasses
from dataclasses import dataclass, replace


@dataclass(frozen=True, kw_only=True)
class ServerConfig:
    host: str
    port: int = 8000
    workers: int = 1
    tls: bool = False
    cert_path: str | None = None

    def __post_init__(self):
        if not self.host.strip():
            raise ValueError("host obrigatório")
        if not 1 <= self.port <= 65535:
            raise ValueError(f"porta inválida: {self.port}")
        if self.workers < 1:
            raise ValueError("workers deve ser >= 1")
        if self.tls and not self.cert_path:
            raise ValueError("tls exige cert_path")
        if self.cert_path and not self.tls:
            raise ValueError("cert_path sem tls")

    @classmethod
    def _check_keys(cls, keys):
        unknown = sorted(set(keys) - {f.name for f in dataclasses.fields(cls)})
        if unknown:
            raise ValueError(f"chaves desconhecidas: {', '.join(unknown)}")

    @classmethod
    def from_dict(cls, data):
        cls._check_keys(data)
        return cls(**data)

    def with_(self, **changes):
        self._check_keys(changes)
        return replace(self, **changes)

    @property
    def url(self):
        scheme, default = ("https", 443) if self.tls else ("http", 80)
        return f"{scheme}://{self.host}" + ("" if self.port == default else f":{self.port}")
