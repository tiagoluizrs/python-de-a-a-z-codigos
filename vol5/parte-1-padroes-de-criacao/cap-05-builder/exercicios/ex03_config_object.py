"""Exercício 3: o "builder" que o Python já tem: argumentos nomeados, ``dataclass`` com validação e ``replace``."""
from dataclasses import dataclass, replace


@dataclass(frozen=True, kw_only=True)
class ServerConfig:
    """Campos (todos só por nome): ``host: str``, ``port: int = 8000``, ``workers: int = 1``, ``tls: bool = False``, ``cert_path: str | None = None``.

    Validação em ``__post_init__`` (vale para qualquer forma de criar), na ORDEM destas regras:

    * ``host`` vazio (ou só espaços): ``ValueError("host obrigatório")``;
    * ``port`` fora de 1 a 65535: ``ValueError(f"porta inválida: {port}")``;
    * ``workers < 1``: ``ValueError("workers deve ser >= 1")``;
    * ``tls`` verdadeiro sem ``cert_path``: ``ValueError("tls exige cert_path")``;
    * ``cert_path`` dado sem ``tls``: ``ValueError("cert_path sem tls")``."""

    host: str
    port: int = 8000
    workers: int = 1
    tls: bool = False
    cert_path: str | None = None

    def __post_init__(self):
        raise NotImplementedError

    @classmethod
    def from_dict(cls, data: dict) -> "ServerConfig":
        """Cria a partir de um dict; chaves que o dataclass não tem: ``ValueError("chaves desconhecidas: a, b")`` (alfabético, antes de criar)."""
        raise NotImplementedError

    def with_(self, **changes) -> "ServerConfig":
        """Uma NOVA configuração com as mudanças aplicadas (``dataclasses.replace``), revalidada. Chave desconhecida: o mesmo ``ValueError`` de ``from_dict``."""
        raise NotImplementedError

    @property
    def url(self) -> str:
        """``http://host:porta`` ou ``https://host:porta`` conforme ``tls``; a porta padrão do esquema (80 em http, 443 em https) é OMITIDA."""
        raise NotImplementedError
